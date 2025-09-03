from flask import Blueprint, request, jsonify
from app.config.database import db_instance
from app.services.right_section import (

    ParibhashikaPadavivaranaService,
    ArthakoshaService,
    BulkUploadService, TatvapadaSuchiService,
)
from app.utils.auth_decorator import login_required

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
def update_padavivarana(samputa, author_id, entry_id):
    data = request.get_json()
    entry = padavivarana_service.update(
        samputa, author_id, entry_id, data.get("content"), data.get("title")
    )
    if entry:
        return jsonify({"success": True, "data": entry})
    return jsonify({"success": False, "error": "Entry not found"}), 404


@right_section_impl_bp.route("/padavivarana/<samputa>/<int:author_id>/<int:entry_id>", methods=["DELETE"])
def delete_padavivarana(samputa, author_id, entry_id):
    success = padavivarana_service.delete(samputa, author_id, entry_id)
    if success:
        return jsonify({"success": True, "message": "Deleted successfully"})
    return jsonify({"success": False, "error": "Entry not found"}), 404


# ----------------- Arthakosha Routes -----------------
@right_section_impl_bp.route("/arthakosha/<samputa>/<author_id>", methods=["GET"])
def get_arthakosha_by_samputa_author(samputa, author_id):
    entries = arthakosha_service.get_by_samputa_author(samputa, int(author_id))
    return jsonify({"success": True, "results": entries})


@right_section_impl_bp.route("/arthakosha", methods=["POST"])
def create_arthakosha():
    data = request.json or {}
    entry = arthakosha_service.create(
        samputa=data["samputa"].strip(),
        author_id=int(data["author_id"]),
        title=data.get("title", "").strip() if data.get("title") else None,
        word=data["word"].strip(),
        meaning=data["meaning"].strip(),
        notes=data.get("notes", "").strip() if data.get("notes") else None
    )
    return jsonify({"success": True, "entry": entry}), 201


@right_section_impl_bp.route("/arthakosha", methods=["GET"])
def list_arthakoshas():
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 10))
    search = request.args.get("search")
    samputa = request.args.get("samputa")
    author_id = request.args.get("author_id")
    if author_id:
        author_id = int(author_id)
    data = arthakosha_service.list(
        samputa=samputa, author_id=author_id, offset=offset, limit=limit, search=search
    )
    return jsonify(data)


@right_section_impl_bp.route("/arthakosha/<samputa>/<author_id>/<arthakosha_id>", methods=["GET"])
def get_arthakosha(samputa, author_id, arthakosha_id):
    entry = arthakosha_service.get(samputa, int(author_id), int(arthakosha_id))
    if entry:
        return jsonify(entry)
    return jsonify({"error": "Word not found"}), 404


@right_section_impl_bp.route("/arthakosha/<samputa>/<author_id>/<arthakosha_id>", methods=["PUT"])
def update_arthakosha(samputa, author_id, arthakosha_id):
    data = request.json or {}
    entry = arthakosha_service.update(
        samputa,
        int(author_id),
        int(arthakosha_id),
        title=data.get("title"),
        word=data.get("word"),
        meaning=data.get("meaning"),
        notes=data.get("notes")
    )
    if entry:
        return jsonify({"message": "Updated successfully", "entry": entry})
    return jsonify({"error": "Word not found"}), 404


@right_section_impl_bp.route("/arthakosha/<samputa>/<author_id>/<arthakosha_id>", methods=["DELETE"])
def delete_arthakosha(samputa, author_id, arthakosha_id):
    success = arthakosha_service.delete(samputa, int(author_id), int(arthakosha_id))
    if success:
        return jsonify({"message": "Deleted successfully"})
    return jsonify({"error": "Word not found"}), 404


# ----------------- Bulk Upload Routes -----------------
@right_section_impl_bp.route("/upload-padavivarana", methods=["POST"])
@login_required
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


@right_section_impl_bp.route("/upload-arthakosha", methods=["POST"])
@login_required
def bulk_upload_arthakosha():
    if "file" not in request.files or request.files["file"].filename.strip() == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    file = request.files["file"]
    records_added, errors = bulk_service.upload_arthakosha(file.stream)
    db_instance.session.commit()
    return jsonify({
        "success": True,
        "message": f"{records_added} Arthakosha record(s) added successfully",
        "errors": errors
    })
