"""
Tatvapada routes: expose endpoints for CRUD operations (API + Web Form).
"""

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.services.tatvapada_service import TatvapadaService
from app.utils.helper import kannada_to_english_digits
from app.utils.logger import setup_logger

# Blueprint and setup
tatvapada_bp = Blueprint("tatvapada", __name__)
logger = setup_logger("tatvapada_routes", "tatvapada_routes.log")
tatvapada_service = TatvapadaService()

# =======================
# JSON API ROUTES
# =======================

@tatvapada_bp.route("/api/tatvapada/add", methods=["POST"])
def add_tatvapada():
    data = request.get_json()
    logger.info(f"Received JSON request: {data}")

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        # Convert Kannada digits if present
        for key in ["samputa_sankhye", "tatvapada_sankhye"]:
            if key in data and isinstance(data[key], str):
                data[key] = int(kannada_to_english_digits(data[key]))
            elif key in data and isinstance(data[key], int):
                # Already English integer, no change needed
                continue
            else:
                # Invalid or missing numeric value
                data[key] = None

        result = tatvapada_service.insert_tatvapada(data)
        if result:
            return jsonify({"message": "Tatvapada inserted", "id": result.id}), 201
        return jsonify({"error": "Insert failed"}), 500

    except IntegrityError:
        return jsonify({
            "error": "Tatvapada already exists with the same Sampuṭa Sankhye, Tatvapada Sankhye, and Tatvapadakara Hesaru."
        }), 409
    except SQLAlchemyError:
        return jsonify({"error": "Database error occurred while inserting the Tatvapada."}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Unexpected error occurred."}), 500


@tatvapada_bp.route("/api/tatvapada/search", methods=["GET"])
def search_tatvapada():
    keyword = request.args.get("keyword", "").strip()
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    results = tatvapada_service.search_by_keyword(keyword)
    return jsonify([
        {k: v for k, v in r.__dict__.items() if not k.startswith("_")}
        for r in results
    ])


@tatvapada_bp.route("/api/tatvapada/sankhyes-by-samputa", methods=["GET"])
def get_tatvapada_sankhye_by_samputa():
    try:
        samputa_sankhye = int(request.args.get("samputa_sankhye", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Valid samputa_sankhye is required"}), 400

    sankhyes = tatvapada_service.get_tatvapada_sankhye_by_samputa(samputa_sankhye)

    if not sankhyes:
        return jsonify({
            "error": f"No tatvapada_sankhye found for samputa_sankhye={samputa_sankhye}"
        }), 404

    return jsonify(sankhyes)



from flask import jsonify
from sqlalchemy.inspection import inspect

@tatvapada_bp.route(
    "/api/tatvapada/<int:samputa_sankhye>/<int:tatvapada_author_id>/<tatvapada_sankhye>",
    methods=["GET"]
)
def get_specific_tatvapada(samputa_sankhye, tatvapada_author_id, tatvapada_sankhye):
    if not (samputa_sankhye and tatvapada_author_id and tatvapada_sankhye):
        return jsonify({"error": "Missing required path parameters"}), 400

    tatvapada = tatvapada_service.get_specific_tatvapada(
        samputa_sankhye, tatvapada_author_id, tatvapada_sankhye
    )

    if tatvapada is None:
        return jsonify({"error": "Tatvapada not found"}), 404

    # Convert SQLAlchemy model to dict
    data = {col.key: getattr(tatvapada, col.key) for col in inspect(tatvapada).mapper.column_attrs}

    # Include related author name (if relationship is present)
    if tatvapada.tatvapadakarara_hesaru:
        data["tatvapadakarara_hesaru"] = tatvapada.tatvapadakarara_hesaru.hesaru

    return jsonify(data)


@tatvapada_bp.route("/api/tatvapada/samputas", methods=["GET"])
def get_all_samputas():
    samputas = tatvapada_service.get_all_samputa_sankhye()
    return jsonify(samputas)

@tatvapada_bp.route("/api/tatvapada/author-sankhyes-by-samputa/<int:samputa_sankhye>", methods=["GET"])
def get_authors_and_sankhyes_by_samputa(samputa_sankhye):
    results = tatvapada_service.get_sankhyes_with_author_by_samputa(samputa_sankhye)

    if not results:
        return jsonify({
            "error": f"No entries found for samputa_sankhye={samputa_sankhye}"
        }), 404

    return jsonify(results)


@tatvapada_bp.route("/api/tatvapada/samputa/<int:samputa_sankhye>", methods=["DELETE"])
def delete_tatvapada_by_samputa(samputa_sankhye):
    """
    Deletes all Tatvapada entries under a specific samputa_sankhye.
    Example: DELETE /api/tatvapada/samputa/1
    """
    try:
        deleted_count = tatvapada_service.delete_tatvapada_by_samputa(samputa_sankhye)

        if deleted_count > 0:
            return jsonify({
                "message": f"{deleted_count} Tatvapada entries deleted for samputa_sankhye = {samputa_sankhye}."
            }), 200
        else:
            return jsonify({
                "message": f"No Tatvapada entries found for samputa_sankhye = {samputa_sankhye}."
            }), 404

    except Exception as e:
        return jsonify({"error": f"Failed to delete entries: {str(e)}"}), 500


@tatvapada_bp.route("/api/tatvapada/<int:samputa_sankhye>/<int:tatvapada_author_id>/<tatvapada_sankhye>", methods=["DELETE"])
def delete_specific_tatvapada(samputa_sankhye, tatvapada_author_id, tatvapada_sankhye):
    """
    Deletes a specific Tatvapada entry using composite key.
    Example: DELETE /api/tatvapada/1/2/4
    """
    try:
        deleted = tatvapada_service.delete_specific_tatvapada(
            samputa_sankhye=samputa_sankhye,
            tatvapada_author_id=tatvapada_author_id,
            tatvapada_sankhye=tatvapada_sankhye
        )

        if deleted:
            return jsonify({
                "message": "Tatvapada deleted successfully."
            }), 200
        else:
            return jsonify({
                "message": "Tatvapada already deleted or not found for given keys.",
                "samputa_sankhye": samputa_sankhye,
                "tatvapada_author_id": tatvapada_author_id,
                "tatvapada_sankhye": tatvapada_sankhye
            }), 404

    except Exception as e:
        return jsonify({"error": f"Failed to delete Tatvapada: {str(e)}"}), 500

# =======================
# WEB FORM ROUTES
# =======================



@tatvapada_bp.route("/tatvapada/add", methods=["GET", "POST"])
def tatvapada_add_form():
    if request.method == "POST":
        form_data = request.get_json() if request.is_json else request.form.to_dict()
        form_data["samputa_sankhye"] = int(form_data.get("samputa_sankhye", 0) or 0)

        success = tatvapada_service.insert_tatvapada(form_data)
        if success:
            return jsonify({"message": "ತತ್ತ್ವಪದ ಯಶಸ್ವಿಯಾಗಿ ಸೇರಿಸಲಾಗಿದೆ."})
        else:
            return jsonify({"error": "ದಾಖಲಾತಿ ವಿಫಲವಾಗಿದೆ."}), 500

    return render_template("insert.html")
