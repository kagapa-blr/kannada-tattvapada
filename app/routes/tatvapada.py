"""
Tatvapada Routes
----------------
This module exposes two groups of routes:
1. JSON API routes: CRUD operations over HTTP (consumed by frontend/clients).
2. Web Form routes: Rendered templates for human-facing forms.
"""

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.inspection import inspect

from app.services.tatvapada_service import TatvapadaService
from app.utils.helper import kannada_to_english_digits
from app.utils.logger import setup_logger

# ------------------------------------
# Setup
# ------------------------------------
tatvapada_bp = Blueprint("tatvapada", __name__)
logger = setup_logger("tatvapada_routes", "tatvapada_routes.log")
tatvapada_service = TatvapadaService()


# ==========================================================
# JSON API ROUTES (CRUD operations, JSON requests/responses)
# ==========================================================

@tatvapada_bp.route("/api/tatvapada/add", methods=["GET", "POST"])
def add_tatvapada():
    """Insert a new Tatvapada entry (form or API JSON)."""
    if request.method == "GET":
        return render_template("add_tatvapada.html")

    data = request.get_json()
    logger.info(f"Received JSON request: {data}")

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        # Normalize numeric fields (store as string, since model expects String)
        for key in ["samputa_sankhye", "tatvapada_sankhye"]:
            if key in data and isinstance(data[key], str):
                normalized = kannada_to_english_digits(data[key]).strip()
                try:
                    if float(normalized).is_integer():
                        data[key] = str(int(float(normalized)))
                    else:
                        data[key] = normalized
                except ValueError:
                    data[key] = normalized
            elif key not in data or data[key] is None:
                data[key] = ""

        # Author name required (id will be resolved in service)
        if not data.get("tatvapadakarara_hesaru"):
            return jsonify({"error": "tatvapadakarara_hesaru is required"}), 400

        result = tatvapada_service.insert_tatvapada(data)
        if result:
            return jsonify({"message": "Tatvapada inserted", "id": result.id}), 201
        return jsonify({"error": "Insert failed"}), 500

    except IntegrityError:
        return jsonify({
            "error": (
                "Tatvapada already exists with the same "
                "samputa_sankhye, tatvapada_sankhye, and tatvapadakarara_hesaru."
            )
        }), 409
    except SQLAlchemyError:
        return jsonify({"error": "Database error occurred while inserting the Tatvapada."}), 500
    except Exception as e:
        logger.error("Unexpected error in add_tatvapada", exc_info=True)
        return jsonify({"error": "Unexpected error occurred."}), 500


@tatvapada_bp.route("/api/tatvapada/search", methods=["POST"])
def search_tatvapada():
    """Search tatvapada entries by keyword."""
    data = request.get_json() or {}
    keyword = data.get("keyword", "").strip()
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    results = tatvapada_service.search_by_keyword(keyword)

    def serialize_tatvapada(t):
        return {
            "id": t.id,
            "samputa_sankhye": t.samputa_sankhye,
            "tatvapadakosha_sheershike": t.tatvapadakosha_sheershike,
            "tatvapada_author_id": t.tatvapada_author_id,
            "tatvapadakarara_hesaru": (
                t.tatvapadakarara_hesaru.tatvapadakarara_hesaru
                if t.tatvapadakarara_hesaru else None
            ),
            "vibhag": t.vibhag,
            "tatvapada_sheershike": t.tatvapada_sheershike,
            "tatvapada_sankhye": t.tatvapada_sankhye,
            "tatvapada_first_line": t.tatvapada_first_line,
            "tatvapada": t.tatvapada,
            "bhavanuvada": t.bhavanuvada,
            "klishta_padagalu_artha": t.klishta_padagalu_artha,
            "tippani": t.tippani,
        }

    return jsonify([serialize_tatvapada(t) for t in results])


@tatvapada_bp.route("/api/tatvapada/sankhyes-by-samputa", methods=["GET"])
def get_tatvapada_sankhye_by_samputa():
    """Fetch tatvapada_sankhyes for a given samputa_sankhye."""
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


@tatvapada_bp.route("/api/tatvapada/update", methods=["PUT"])
def update_tatvapada_by_composite_keys():
    """Update a tatvapada entry using composite keys."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        required_keys = ["samputa_sankhye", "tatvapada_sankhye", "tatvapada_author_id"]
        for key in required_keys:
            if key not in data:
                return jsonify({"error": f"Missing required field: {key}"}), 400

        updated_entry = tatvapada_service.update_by_composite_keys(
            data["samputa_sankhye"], data["tatvapada_sankhye"], data["tatvapada_author_id"], data
        )

        return jsonify({
            "message": "Tatvapada updated successfully",
            "updated_entry": {
                "tatvapadakosha_sheershike": updated_entry.tatvapadakosha_sheershike,
                "tatvapada_sheershike": updated_entry.tatvapada_sheershike,
                "tatvapada_author_id": updated_entry.tatvapada_author_id,
                "tatvapadakarara_hesaru": (
                    updated_entry.tatvapadakarara_hesaru.tatvapadakarara_hesaru
                    if updated_entry.tatvapadakarara_hesaru else None
                ),
                "tatvapada_sankhye": updated_entry.tatvapada_sankhye,
                "tatvapada_first_line": updated_entry.tatvapada_first_line,
                "tatvapada": updated_entry.tatvapada,
                "klishta_padagalu_artha": updated_entry.klishta_padagalu_artha,
                "tippani": updated_entry.tippani,
                "bhavanuvada": updated_entry.bhavanuvada,
                "vibhag": updated_entry.vibhag,
            }
        })

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except SQLAlchemyError as db_err:
        return jsonify({"error": f"Database error: {str(db_err)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@tatvapada_bp.route(
    "/api/tatvapada/<int:samputa_sankhye>/<int:tatvapada_author_id>/<tatvapada_sankhye>",
    methods=["GET"]
)
def get_specific_tatvapada(samputa_sankhye, tatvapada_author_id, tatvapada_sankhye):
    """Fetch a single Tatvapada by composite keys."""
    tatvapada = tatvapada_service.get_specific_tatvapada(
        samputa_sankhye, tatvapada_author_id, tatvapada_sankhye
    )

    if tatvapada is None:
        return jsonify({"error": "Tatvapada not found"}), 404

    data = {col.key: getattr(tatvapada, col.key) for col in inspect(tatvapada).mapper.column_attrs}
    if tatvapada.tatvapadakarara_hesaru:
        data["tatvapadakarara_hesaru"] = tatvapada.tatvapadakarara_hesaru.tatvapadakarara_hesaru

    return jsonify(data)


@tatvapada_bp.route("/api/tatvapada/samputas", methods=["GET"])
def get_all_samputas():
    """Return distinct list of all samputa_sankhyes."""
    return jsonify(tatvapada_service.get_all_samputa_sankhye())


@tatvapada_bp.route("/api/tatvapada/author-sankhyes-by-samputa/<int:samputa_sankhye>", methods=["GET"])
def get_authors_and_sankhyes_by_samputa(samputa_sankhye):
    """Return authors and their tatvapada_sankhyes for given samputa."""
    results = tatvapada_service.get_sankhyes_with_author_by_samputa(samputa_sankhye)
    if not results:
        return jsonify({
            "error": f"No entries found for samputa_sankhye={samputa_sankhye}"
        }), 404
    return jsonify(results)


@tatvapada_bp.route("/api/tatvapada/samputa/<int:samputa_sankhye>", methods=["DELETE"])
def delete_tatvapada_by_samputa(samputa_sankhye):
    """Delete all tatvapadas under a given samputa."""
    try:
        deleted_count = tatvapada_service.delete_tatvapada_by_samputa(samputa_sankhye)
        if deleted_count > 0:
            return jsonify({
                "message": f"{deleted_count} Tatvapada entries deleted for samputa_sankhye = {samputa_sankhye}."
            }), 200
        return jsonify({
            "message": f"No Tatvapada entries found for samputa_sankhye = {samputa_sankhye}."
        }), 404
    except Exception as e:
        return jsonify({"error": f"Failed to delete entries: {str(e)}"}), 500


@tatvapada_bp.route(
    "/api/tatvapada/delete/<string:samputa_sankhye>/<string:tatvapada_sankhye>/<int:tatvapada_author_id>",
    methods=["DELETE"]
)
def delete_specific_tatvapada(samputa_sankhye, tatvapada_sankhye, tatvapada_author_id):
    """Delete a specific tatvapada by composite keys."""
    try:
        try:
            samputa_sankhye_val = float(samputa_sankhye)
        except ValueError:
            raise ValueError("Invalid samputa_sankhye. Must be a number.")

        deleted = tatvapada_service.delete_by_composite_keys(
            samputa_sankhye_val, tatvapada_sankhye, tatvapada_author_id
        )

        if deleted:
            return jsonify({"message": "Tatvapada entry deleted successfully"}), 200
        return jsonify({"error": "Tatvapada entry not found"}), 404

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@tatvapada_bp.route("/api/tatvapada/delete-keys", methods=["GET"])
def get_delete_keys():
    """Return all delete keys (composite identifiers) for tatvapada entries."""
    try:
        keys = tatvapada_service.get_all_delete_keys()
        return jsonify({"delete_keys": keys}), 200
    except Exception as e:
        tatvapada_service.logger.error(f"Error fetching delete keys: {e}")
        return jsonify({"error": "Failed to fetch delete keys"}), 500


# ==========================================================
# WEB FORM ROUTES (Template rendering for human interaction)
# ==========================================================

@tatvapada_bp.route("/tatvapada/add", methods=["GET"])
def tatvapada_add_form():
    """Render web form for adding a Tatvapada."""
    return render_template("admin_tabs/add_tatvapada.html")


@tatvapada_bp.route("/tatvapada/update", methods=["GET", "POST"])
def tatvapada_update_form():
    """Render web form for updating a Tatvapada."""
    return render_template("admin_tabs/update_tatvapada.html")
