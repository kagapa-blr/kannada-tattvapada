from flask import Blueprint
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app.config.database import db_instance
from app.services.right_section import (

    ParibhashikaPadavivaranaService,
    ArthakoshaService,
    BulkUploadService, TatvapadaSuchiService,
)
from app.utils.auth_decorator import admin_required

# Blueprint with url_prefix for API versioning
right_section_impl_bp = Blueprint(
    "right_section_impl", __name__, url_prefix="/api/v1/right-section"
)

# Initialize services
tatvapada_service = TatvapadaSuchiService()
padavivarana_service = ParibhashikaPadavivaranaService()
arthakosha_service = ArthakoshaService()
bulk_service = BulkUploadService(db_instance.session)


# ----------------- Tatvapada Routes -----------------
@right_section_impl_bp.route("/tatvapadasuchi", methods=["GET"])
def list_tatvapadas():
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 10))
    search = request.args.get("search", "").strip()
    MAX_LIMIT = 100
    if limit > MAX_LIMIT:
        limit = MAX_LIMIT

    data = tatvapada_service.get_tatvapada_suchi(offset, limit, search)
    next_offset = offset + limit if (offset + limit) < data["total"] else None
    prev_offset = offset - limit if offset - limit >= 0 else None

    return jsonify({
        "offset": offset,
        "limit": limit,
        "count": len(data["results"]),
        "total": data["total"],
        "next_offset": next_offset,
        "prev_offset": prev_offset,
        "data": data["results"]
    })


@right_section_impl_bp.route("/tatvapada", methods=["GET"])
def get_tatvapada():
    samputa = request.args.get("samputa_sankhye")
    author_id = request.args.get("tatvapada_author_id")
    number = request.args.get("tatvapada_sankhye")

    if not samputa or not author_id or not number:
        return jsonify({"error": "samputa_sankhye, tatvapada_author_id, and tatvapada_sankhye are required"}), 400

    try:
        record = tatvapada_service.get_tatvapada_details(samputa, int(author_id), number)
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

    if not record:
        return jsonify({"error": "Tatvapada not found"}), 404
    return jsonify(record)


# ----------------- Paribhashika Padavivarana Routes -----------------
@right_section_impl_bp.route("/samputa-authors", methods=["GET"])
def get_samputa_authors():
    try:
        data = tatvapada_service.get_samputa_with_authors()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@right_section_impl_bp.route("/padavivarana", methods=["GET"])
def get_all_padavivarana():
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 10))
    search = request.args.get("search", "")
    data = padavivarana_service.get_all(offset, limit, search)
    return jsonify(data)


@right_section_impl_bp.route("/padavivarana/<samputa>/<author_id>", methods=["GET"])
def get_padavivarana_id_by_samputa_author(samputa, author_id):
    entries = padavivarana_service.get_id_title(samputa, int(author_id))
    return jsonify({"success": True, "data": entries})


@right_section_impl_bp.route("/padavivarana/<samputa>/<author_id>/<int:entry_id>", methods=["GET"])
def get_padavivarana(samputa, author_id, entry_id):
    entry = padavivarana_service.get_entry(samputa, int(author_id), entry_id)
    if entry:
        return jsonify(entry)
    return jsonify({"error": "Entry not found"}), 404


@right_section_impl_bp.route("/padavivarana", methods=["POST"])
@admin_required
def create_padavivarana():
    data = request.get_json()
    try:
        entry = padavivarana_service.create(
            samputa=data["samputa"],
            author_id=int(data["author_id"]),
            content=data["content"],
            title=data["title"]
        )
        return jsonify({"success": True, "data": entry}), 201
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@right_section_impl_bp.route("/padavivarana/<samputa>/<int:author_id>/<int:entry_id>", methods=["PUT"])
@admin_required
def update_padavivarana(samputa, author_id, entry_id):
    data = request.get_json()
    entry = padavivarana_service.update(
        samputa, author_id, entry_id, data.get("content"), data.get("title")
    )
    if entry:
        return jsonify({"success": True, "data": entry})
    return jsonify({"success": False, "error": "Entry not found"}), 404


@right_section_impl_bp.route("/padavivarana/<samputa>/<int:author_id>/<int:entry_id>", methods=["DELETE"])
@admin_required
def delete_padavivarana(samputa, author_id, entry_id):
    success = padavivarana_service.delete(samputa, author_id, entry_id)
    if success:
        return jsonify({"success": True, "message": "Deleted successfully"})
    return jsonify({"success": False, "error": "Entry not found"}), 404

@right_section_impl_bp.route("/upload-padavivarana", methods=["POST"])
@admin_required
def bulk_upload_padavivarana():
    if "file" not in request.files or request.files["file"].filename.strip() == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    file = request.files["file"]
    records_added, errors = bulk_service.upload_paribhashika_padavivarana(file.stream)
    db_instance.session.commit()
    return jsonify({
        "success": True,
        "message": f"{records_added} Padavivarana record(s) added successfully",
        "errors": errors
    })


# ----------------- Arthakosha Routes -----------------
@right_section_impl_bp.route("/arthakosha/<samputa>/<int:author_id>", methods=["GET"])
def get_arthakosha_by_samputa_author(samputa, author_id):
    entries = ArthakoshaService.get_by_samputa_author(
        samputa=samputa.strip(),
        author_id=author_id
    )
    return jsonify({"success": True, "results": entries})


@right_section_impl_bp.route("/arthakosha", methods=["POST"])
@admin_required
def create_arthakosha():
    data = request.get_json(silent=True) or {}

    try:
        entry = ArthakoshaService.create(
            samputa=(data.get("samputa") or "").strip(),
            author_id=data.get("author_id"),
            word=(data.get("word") or "").strip(),
            meaning=(data.get("meaning") or "").strip(),
            notes=(data.get("notes") or "").strip() or None
        )
        return jsonify({"success": True, "entry": entry}), 201

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    except SQLAlchemyError:
        return jsonify({"success": False, "message": "Database error occurred while creating Arthakosha"}), 500

    except Exception:
        return jsonify({"success": False, "message": "Failed to create Arthakosha"}), 500


@right_section_impl_bp.route("/arthakosha", methods=["GET"])
@admin_required
def list_arthakoshas():
    try:
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 10))
        search = (request.args.get("search") or "").strip()
        samputa = (request.args.get("samputa") or "").strip()

        author_id = request.args.get("author_id")
        author_id = int(author_id) if author_id and str(author_id).isdigit() else None

        data = ArthakoshaService.list(
            samputa=samputa or None,
            author_id=author_id,
            offset=offset,
            limit=limit,
            search=search or None
        )
        return jsonify({"success": True, **data})

    except Exception:
        return jsonify({"success": False, "message": "Failed to list Arthakosha entries"}), 500


@right_section_impl_bp.route("/arthakosha/<samputa>/<int:author_id>/<int:arthakosha_id>", methods=["GET"])
@admin_required
def get_arthakosha(samputa, author_id, arthakosha_id):
    entry = ArthakoshaService.get(
        samputa=samputa.strip(),
        author_id=author_id,
        id=arthakosha_id
    )
    if entry:
        return jsonify({"success": True, "entry": entry})
    return jsonify({"success": False, "message": "Arthakosha entry not found"}), 404


@right_section_impl_bp.route("/arthakosha/<samputa>/<int:author_id>/<int:arthakosha_id>", methods=["PUT"])
@admin_required
def update_arthakosha(samputa, author_id, arthakosha_id):
    data = request.get_json(silent=True) or {}

    try:
        entry = ArthakoshaService.update(
            samputa=samputa.strip(),
            author_id=author_id,
            id=arthakosha_id,
            word=(data.get("word") or "").strip() if data.get("word") is not None else None,
            meaning=(data.get("meaning") or "").strip() if data.get("meaning") is not None else None,
            notes=(data.get("notes") or "").strip() if data.get("notes") is not None else None
        )

        if entry:
            return jsonify({"success": True, "message": "Updated successfully", "entry": entry})

        return jsonify({"success": False, "message": "Arthakosha entry not found"}), 404

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    except SQLAlchemyError:
        return jsonify({"success": False, "message": "Database error occurred while updating Arthakosha"}), 500

    except Exception:
        return jsonify({"success": False, "message": "Failed to update Arthakosha"}), 500


@right_section_impl_bp.route("/arthakosha/<samputa>/<int:author_id>/<int:arthakosha_id>", methods=["DELETE"])
@admin_required
def delete_arthakosha(samputa, author_id, arthakosha_id):
    try:
        success = ArthakoshaService.delete(
            samputa=samputa.strip(),
            author_id=author_id,
            id=arthakosha_id
        )
        if success:
            return jsonify({"success": True, "message": "Deleted successfully"})
        return jsonify({"success": False, "message": "Arthakosha entry not found"}), 404

    except SQLAlchemyError:
        return jsonify({"success": False, "message": "Database error occurred while deleting Arthakosha"}), 500

    except Exception:
        return jsonify({"success": False, "message": "Failed to delete Arthakosha"}), 500


@right_section_impl_bp.route("/upload-arthakosha", methods=["POST"])
@admin_required
def bulk_upload_arthakosha():
    if "file" not in request.files or not request.files["file"].filename.strip():
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400

    file = request.files["file"]

    records_added, errors = bulk_service.upload_arthakosha(file.stream)

    status_code = 200 if records_added > 0 else 400

    return jsonify({
        "success": records_added > 0,
        "message": f"{records_added} Arthakosha record(s) added successfully" if records_added else "No records were added",
        "errors": errors
    }), status_code


