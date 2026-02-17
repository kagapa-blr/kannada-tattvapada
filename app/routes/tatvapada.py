"""
Tatvapada Routes
----------------
This module organizes routes into 3 clear groups:
1. JSON API routes (CRUD + search + utilities)
2. Web Form routes (admin interaction templates)
3. Bulk Upload routes (CSV import)
"""
from flask import Blueprint, request, jsonify, render_template
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.inspection import inspect

from app.config.database import db_instance
from app.services.tatvapada_service import TatvapadaService, BulkService
from app.utils.auth_decorator import login_required, admin_required
from app.utils.helper import kannada_to_english_digits
from app.utils.logger import setup_logger

# ==========================================================
# Setup
# ==========================================================
tatvapada_bp = Blueprint("tatvapada", __name__)
logger = setup_logger("tatvapada_routes")

tatvapada_service = TatvapadaService()
bulk_service = BulkService(db_instance.session)


# ==========================================================
# Helpers
# ==========================================================
def _serialize_tatvapada(t):
    """Serialize Tatvapada SQLAlchemy object to dict for JSON response."""
    return {
        "id": t.id,
        "samputa_sankhye": t.samputa_sankhye,
        "tatvapadakosha_sheershike": t.tatvapadakosha_sheershike,
        "tatvapada_author_id": t.tatvapada_author_id,
        "tatvapadakarara_hesaru": (
            t.tatvapadakarara_hesaru.tatvapadakarara_hesaru if t.tatvapadakarara_hesaru else None
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


# ==========================================================
# JSON API ROUTES (CRUD + Search + Utilities)
# ==========================================================

# ---------- CREATE ----------
@tatvapada_bp.route("/api/tatvapada/add", methods=["POST"])
@admin_required
def add_tatvapada():
    """Insert a new Tatvapada entry."""
    # if request.method == "GET":
    #     return render_template("add_tatvapada.html")

    data = request.get_json()
    logger.info(f"Received JSON request: {data}")

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        # Normalize numeric fields
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

        # Author validation
        if not data.get("tatvapadakarara_hesaru"):
            return jsonify({"error": "tatvapadakarara_hesaru is required"}), 400

        result = tatvapada_service.insert_tatvapada(data)
        if result:
            return jsonify({"message": "Tatvapada inserted", "id": result.id}), 201
        return jsonify({"error": "Insert failed"}), 500

    except IntegrityError:
        return jsonify({
            "error": "Tatvapada already exists with the same samputa_sankhye, tatvapada_sankhye, and tatvapadakarara_hesaru."
        }), 409
    except SQLAlchemyError:
        return jsonify({"error": "Database error occurred while inserting"}), 500
    except Exception:
        logger.error("Unexpected error in add_tatvapada", exc_info=True)
        return jsonify({"error": "Unexpected error occurred."}), 500


# ---------- BULK UPDATE ----------
@tatvapada_bp.route("/api/tatvapada/bulk-update", methods=["POST"])
@admin_required
def bulk_update_tatvapada():
    """
    Bulk update Tatvapada records from CSV upload.
    Expects multipart/form-data with file field: 'file'
    Matching: samputa_sankhye + tatvapada_sankhye + tatvapadakarara_hesaru
    """
    if "file" not in request.files:
        return jsonify({"error": "CSV file is required"}), 400

    file = request.files["file"]

    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files are supported"}), 400

    try:
        records_updated, errors = tatvapada_service.bulk_service.update_csv_records(file)

        response = {
            "records_updated": records_updated,
            "errors": errors
        }

        # Partial success
        if errors and records_updated > 0:
            return jsonify(response), 207  # Multi-Status

        # Full success
        if records_updated > 0 and not errors:
            return jsonify(response), 200

        # Full failure (no records updated)
        return jsonify(response), 400

    except Exception:
        logger.error("Unexpected error in bulk_update_tatvapada", exc_info=True)
        return jsonify({"error": "Unexpected error occurred during bulk update."}), 500


# ---------- SEARCH TATVAPADA ----------
@tatvapada_bp.route("/api/tatvapada/search", methods=["POST"])
def search_tatvapada():
    """
    Search Tatvapada entries by keyword with optional samputa/author filters and pagination.
    """
    data = request.get_json() or {}
    tatvapada_service.logger.info(f"Received search payload: {data}")

    keyword = (data.get("keyword") or "").strip()
    samputa = (data.get("samputa") or "").strip() or None
    author_id = data.get("author_id", None)

    offset = max(int(data.get("offset", 0)), 0)
    limit = min(max(int(data.get("limit", 10)), 1), 100)

    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    try:
        results, total = tatvapada_service.search_by_keyword(
            keyword=keyword,
            offset=offset,
            limit=limit,
            samputa=samputa,
            author_id=int(author_id) if author_id else None
        )

        return jsonify({
            "results": [_serialize_tatvapada(t) for t in results],
            "pagination": {
                "total": total,
                "offset": offset,
                "limit": limit,
                "has_more": (offset + limit) < total
            }
        })

    except Exception as e:
        tatvapada_service.logger.error(
            f"Error in search_tatvapada route (keyword='{keyword}', samputa={samputa}, author_id={author_id}): {e}"
        )
        return jsonify({"error": "Internal server error"}), 500


@tatvapada_bp.route("/api/tatvapada/<samputa_sankhye>/<tatvapada_author_id>/<tatvapada_sankhye>", methods=["GET"])
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


@tatvapada_bp.route("/api/tatvapada/sankhyes-by-samputa", methods=["GET"])
def get_tatvapada_sankhye_by_samputa():
    """List tatvapada_sankhyes for a given samputa_sankhye."""
    try:
        samputa_sankhye = int(request.args.get("samputa_sankhye", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Valid samputa_sankhye is required"}), 400

    sankhyes = tatvapada_service.get_tatvapada_sankhye_by_samputa(samputa_sankhye)
    if not sankhyes:
        return jsonify({"error": f"No tatvapada_sankhye found for samputa_sankhye={samputa_sankhye}"}), 404
    return jsonify(sankhyes)


@tatvapada_bp.route("/api/tatvapada/samputas", methods=["GET"])
def get_all_samputas():
    """Return distinct list of all samputa_sankhyes."""
    return jsonify(tatvapada_service.get_all_samputa_sankhye())


@tatvapada_bp.route("/api/tatvapada/author-sankhyes-by-samputa/<samputa_sankhye>", methods=["GET"])
def get_authors_and_sankhyes_by_samputa(samputa_sankhye):
    """Return authors and their tatvapada_sankhyes for a samputa."""
    results = tatvapada_service.get_sankhyes_with_author_by_samputa(samputa_sankhye)
    if not results:
        return jsonify({"error": f"No entries found for samputa_sankhye={samputa_sankhye}"}), 404
    return jsonify(results)


# ---------- UPDATE ----------
@tatvapada_bp.route("/api/tatvapada/update", methods=["PUT"])
@admin_required
def update_tatvapada_by_composite_keys():
    """Update a tatvapada entry using composite keys."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        for key in ["samputa_sankhye", "tatvapada_sankhye", "tatvapada_author_id"]:
            if key not in data:
                return jsonify({"error": f"Missing required field: {key}"}), 400

        updated_entry = tatvapada_service.update_by_composite_keys(
            data["samputa_sankhye"], data["tatvapada_sankhye"], data["tatvapada_author_id"], data
        )

        return jsonify(
            {"message": "Tatvapada updated successfully", "updated_entry": _serialize_tatvapada(updated_entry)})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except SQLAlchemyError as db_err:
        return jsonify({"error": f"Database error: {str(db_err)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# ---------- DELETE ----------
@tatvapada_bp.route("/tatvapada/delete-by-samputa/<samputa_sankhye>", methods=["DELETE"])
@admin_required
def delete_tatvapada_by_samputa(samputa_sankhye):
    """Delete all tatvapadas under a samputa."""
    try:
        deleted_count = tatvapada_service.delete_tatvapada_by_samputa(samputa_sankhye)
        if deleted_count > 0:
            return jsonify({"message": f"{deleted_count} entries deleted for samputa={samputa_sankhye}."})
        return jsonify({"message": f"No entries found for samputa={samputa_sankhye}."}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to delete entries: {str(e)}"}), 500


@tatvapada_bp.route(
    "/api/tatvapada/delete/<string:samputa_sankhye>/<string:tatvapada_sankhye>/<int:tatvapada_author_id>",
    methods=["DELETE"])
@admin_required
def delete_specific_tatvapada(samputa_sankhye, tatvapada_sankhye, tatvapada_author_id):
    """Delete a single tatvapada by composite keys."""
    try:
        samputa_sankhye_val = float(samputa_sankhye)
        deleted = tatvapada_service.delete_by_composite_keys(samputa_sankhye_val, tatvapada_sankhye,
                                                             tatvapada_author_id)
        if deleted:
            return jsonify({"message": "Tatvapada entry deleted successfully"})
        return jsonify({"error": "Tatvapada entry not found"}), 404
    except ValueError:
        return jsonify({"error": "Invalid samputa_sankhye. Must be a number."}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@tatvapada_bp.route("/api/tatvapada/delete-keys", methods=["GET"])
def get_delete_keys():
    """Fetch all composite keys for deletion."""
    try:
        keys = tatvapada_service.get_all_delete_keys()
        return jsonify({"delete_keys": keys}), 200
    except Exception as e:
        tatvapada_service.logger.error(f"Error fetching delete keys: {e}")
        return jsonify({"error": "Failed to fetch delete keys"}), 500


# ==========================================================
# WEB FORM ROUTES (Admin templates)
# ==========================================================

@tatvapada_bp.route("/tatvapada/add", methods=["GET"])
@admin_required
def tatvapada_add_form():
    """Admin form: add a Tatvapada."""
    return render_template("admin_tabs/add_tatvapada.html")


@tatvapada_bp.route("/tatvapada/update", methods=["GET", "POST"])
@admin_required
def tatvapada_update_form():
    """Admin form: update a Tatvapada."""
    return render_template("admin_tabs/update_tatvapada.html")


# ==========================================================
# BULK UPLOAD ROUTES
# ==========================================================

@tatvapada_bp.route("/bulk-upload", methods=["POST"])
@admin_required
def bulk_upload():
    """Handle CSV bulk upload of Tatvapada + authors."""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400

    try:
        records_added, errors = bulk_service.upload_csv_records(file)
        db_instance.session.commit()
        return jsonify({"success": True, "message": f"{records_added} records added", "errors": errors}), 200
    except Exception as e:
        db_instance.session.rollback()
        return jsonify({"success": False, "message": "Failed to insert CSV records", "error": str(e)}), 500
