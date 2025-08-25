from flask import Blueprint, request, jsonify

from app.config.database import db_instance
from app.services.right_section import RightSection, RightSectionBulkService
from app.utils.auth_decorator import login_required

# Blueprint with url_prefix for API versioning
right_section_impl_bp = Blueprint("right_section_impl", __name__, url_prefix="/api/v1/right-section")


right_section = RightSection()
right_section_bulk_service = RightSectionBulkService(db_instance.session)
# ----------------- Tatvapada Routes ----------------- #

# 1️⃣ List all Tatvapadas (paginated, optional search)
@right_section_impl_bp.route("/tatvapadasuchi", methods=["GET"])
def list_tatvapadas():
    """
    GET /api/v1/right-section/tatvapadasuchi?offset=0&limit=10&search=word
    Returns paginated list of tatvapadas with optional search filter.
    """
    try:
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 10))
        search = request.args.get("search", "").strip()

        MAX_LIMIT = 100
        if limit > MAX_LIMIT:
            limit = MAX_LIMIT

    except ValueError:
        return jsonify({"error": "Invalid offset or limit"}), 400

    try:
        data = right_section.get_tatvapada_suchi(offset=offset, limit=limit, search=search)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Server error", "details": str(e)}), 500

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


# 2️⃣ Get a specific Tatvapada by samputa, author, and number (with Tippanis)
@right_section_impl_bp.route("/tatvapada", methods=["GET"])
def get_tatvapada():
    """
    GET /api/v1/right-section/tatvapada?samputa_sankhye=1&tatvapada_author_id=2&tatvapada_sankhye=5
    Fetches a particular tatvapada entry with Tippanis.
    """
    samputa = request.args.get("samputa_sankhye")
    author_id = request.args.get("tatvapada_author_id")
    number = request.args.get("tatvapada_sankhye")

    if not samputa or not author_id or not number:
        return jsonify({"error": "samputa_sankhye, tatvapada_author_id, and tatvapada_sankhye are required"}), 400

    try:
        author_id = int(author_id)
    except ValueError:
        return jsonify({"error": "tatvapada_author_id must be an integer"}), 400

    try:
        record = right_section.get_tatvapada_details(
            samputa_sankhye=samputa,
            tatvapada_author_id=author_id,
            tatvapada_sankhye=number,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Server error", "details": str(e)}), 500

    if not record:
        return jsonify({"error": "Tatvapada not found"}), 404

    return jsonify(record)






# ----------------- Tippani Routes ----------------- #

@right_section_impl_bp.route("/tippani", methods=["GET"])
def get_tippani():
    """
    GET /tippani
    Behavior:
    - If `samputa` and `author_id` are provided: return tippanis for that author+samputa.
    - Otherwise: return paginated full list (optional `offset`, `limit`, `search`).
    """
    try:
        samputa = request.args.get("samputa")
        author_id = request.args.get("author_id", type=int)

        if samputa and author_id:
            # Author-specific request
            data = right_section.get_tippanis_by_samputa_author(samputa, author_id)
            return jsonify({"success": True, "data": data})

        # Paginated list request
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 10))
        search = request.args.get("search", "")

        results = right_section.get_all_tippanis(offset=offset, limit=limit, search=search)

        # Always return 200; frontend handles empty results
        if not results.get("results"):
            return jsonify({
                "success": False,
                "message": "No Tippanis found",
                "results": [],
                "offset": offset,
                "limit": limit,
                "total": 0
            }), 200

        return jsonify({"success": True, **results})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# 3. Get Samputa → Authors mapping
@right_section_impl_bp.route("/samputa-authors", methods=["GET"])
def get_samputa_authors():
    """
    GET /api/v1/right-section/samputa-authors
    Returns list of Samputa numbers with their associated authors.
    """
    try:
        data = right_section.get_samputa_with_authors()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# 4. Get specific Tippani by Samputa + Author + Tippani ID
@right_section_impl_bp.route("/tippani/<int:tippani_id>", methods=["GET"])
def get_specific_tippani(tippani_id):
    """
    GET /api/v1/right-section/tippani/<tippani_id>?samputa=1&author_id=2
    Returns details of a specific Tippani.
    """
    samputa = request.args.get("samputa")
    author_id = request.args.get("author_id", type=int)

    if not samputa or not author_id:
        return jsonify({"success": False, "message": "samputa and author_id required"}), 400

    data = right_section.get_tippani(samputa, author_id, tippani_id)
    if not data:
        return jsonify({"success": False, "message": "Tippani not found"}), 404

    return jsonify({"success": True, "data": data})


# 5. Create new Tippani
@right_section_impl_bp.route("/tippani", methods=["POST"])
def create_tippani():
    """
    POST /api/v1/right-section/tippani
    Body: { "samputa": "1", "author_id": 2, "title": "optional", "content": "..." }
    Creates a new Tippani.
    """
    body = request.json
    samputa = body.get("samputa")
    author_id = body.get("author_id")
    title = body.get("title")  # optional
    content = body.get("content")

    try:
        data = right_section.create_tippani(samputa, author_id, content, title)
        return jsonify({"success": True, "data": data})
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# 6. Update Tippani by Samputa + Author + Tippani ID
@right_section_impl_bp.route("/tippani/<int:tippani_id>", methods=["PUT"])
def update_tippani(tippani_id):
    """
    PUT /api/v1/right-section/tippani/<tippani_id>
    Body: { "samputa": "1", "author_id": 2, "title": "optional", "content": "..." }
    Updates an existing Tippani.
    """
    body = request.json
    samputa = body.get("samputa")
    author_id = body.get("author_id")
    content = body.get("content")
    title = body.get("title")  # optional

    if not samputa or not author_id:
        return jsonify({"success": False, "message": "samputa and author_id required"}), 400
    if content is None and title is None:
        return jsonify({"success": False, "message": "Either content or title is required"}), 400

    data = right_section.update_tippani(samputa, author_id, tippani_id, content, title)
    if data:
        return jsonify({"success": True, "data": data})
    return jsonify({"success": False, "message": "Tippani not found"}), 404


# 7. Delete Tippani by Samputa + Author + Tippani ID
@right_section_impl_bp.route("/tippani/<int:tippani_id>", methods=["DELETE"])
def delete_tippani(tippani_id):
    """
    DELETE /api/v1/right-section/tippani/<tippani_id>
    Body: { "samputa": "1", "author_id": 2 }
    Deletes a specific Tippani.
    """
    body = request.json
    samputa = body.get("samputa")
    author_id = body.get("author_id")

    if not samputa or not author_id:
        return jsonify({"success": False, "message": "samputa and author_id required"}), 400

    deleted = right_section.delete_tippani(samputa, author_id, tippani_id)
    if deleted:
        return jsonify({"success": True, "message": "Tippani deleted successfully"})
    return jsonify({"success": False, "message": "Tippani not found"}), 404




# ---------------- Arthakosha Routes ----------------
@right_section_impl_bp.route('/arthakosha', methods=['POST'])
def create_arthakosha():
    data = request.json or {}
    required_fields = ['samputa', 'author_id', 'word', 'meaning']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "samputa, author_id, word, and meaning are required"}), 400

    try:
        entry = right_section.create_arthakosha(
            samputa=str(data['samputa']).strip(),
            author_id=int(data['author_id']),
            title=str(data.get('title')).strip() if data.get('title') else None,
            word=str(data['word']).strip(),
            meaning=str(data['meaning']).strip(),
            notes=str(data.get('notes')).strip() if data.get('notes') else None
        )
        return jsonify(entry), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@right_section_impl_bp.route('/arthakosha', methods=['GET'])
def list_arthakoshas():
    try:
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 10))
        search = request.args.get('search')
        samputa = request.args.get('samputa')
        author_id = request.args.get('author_id')
        if author_id:
            author_id = int(author_id)
    except ValueError:
        return jsonify({"error": "Invalid offset, limit, or author_id"}), 400

    data = right_section.list_arthakoshas(
        samputa=str(samputa).strip() if samputa else None,
        author_id=int(author_id) if author_id else None,
        offset=offset,
        limit=limit,
        search=str(search).strip() if search else None
    )
    return jsonify(data)


@right_section_impl_bp.route('/arthakosha/<samputa>/<author_id>/<arthakosha_id>', methods=['GET'])
def get_arthakosha(samputa, author_id, arthakosha_id):
    try:
        author_id = int(author_id)
        arthakosha_id = int(arthakosha_id)
    except ValueError:
        return jsonify({"error": "author_id and arthakosha_id must be integers"}), 400

    entry = right_section.get_arthakosha(str(samputa).strip(), author_id, arthakosha_id)
    if not entry:
        return jsonify({"error": "Word not found"}), 404
    return jsonify(entry)


@right_section_impl_bp.route('/arthakosha/<samputa>/<author_id>/<arthakosha_id>', methods=['PUT'])
def update_arthakosha(samputa, author_id, arthakosha_id):
    data = request.json or {}
    try:
        author_id = int(author_id)
        arthakosha_id = int(arthakosha_id)
    except ValueError:
        return jsonify({"error": "author_id and arthakosha_id must be integers"}), 400

    entry = right_section.update_arthakosha(
        samputa=str(samputa).strip(),
        author_id=author_id,
        arthakosha_id=arthakosha_id,
        title=str(data.get('title')).strip() if data.get('title') else None,
        word=str(data.get('word')).strip() if data.get('word') else None,
        meaning=str(data.get('meaning')).strip() if data.get('meaning') else None,
        notes=str(data.get('notes')).strip() if data.get('notes') else None
    )
    if not entry:
        return jsonify({"error": "Word not found"}), 404
    return jsonify({"message": "Updated successfully", "entry": entry})


@right_section_impl_bp.route('/arthakosha/<samputa>/<author_id>/<arthakosha_id>', methods=['DELETE'])
def delete_arthakosha(samputa, author_id, arthakosha_id):
    try:
        author_id = int(author_id)
        arthakosha_id = int(arthakosha_id)
    except ValueError:
        return jsonify({"error": "author_id and arthakosha_id must be integers"}), 400

    success = right_section.delete_arthakosha(str(samputa).strip(), author_id, arthakosha_id)
    if not success:
        return jsonify({"error": "Word not found"}), 404
    return jsonify({"message": "Deleted successfully"})





@right_section_impl_bp.route("/upload-tippani", methods=["POST"])
@login_required
def bulk_upload_tippani():
    """Handle CSV bulk upload of Tatvapada Tippani."""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400

    try:
        records_added, errors = right_section_bulk_service.upload_tippani_records(file)
        db_instance.session.commit()
        return jsonify({
            "success": True,
            "message": f"{records_added} Tippani records added",
            "errors": errors
        }), 200
    except Exception as e:
        db_instance.session.rollback()
        return jsonify({
            "success": False,
            "message": "Failed to insert Tippani CSV records",
            "error": str(e)
        }), 500


@right_section_impl_bp.route("/upload-arthakosha", methods=["POST"])
@login_required
def bulk_upload_arthakosha():
    """Handle CSV bulk upload of Arthakosha entries."""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400

    try:
        records_added, errors = right_section_bulk_service.upload_arthakosha_records(file)
        db_instance.session.commit()
        return jsonify({
            "success": True,
            "message": f"{records_added} Arthakosha records added",
            "errors": errors
        }), 200
    except Exception as e:
        db_instance.session.rollback()
        return jsonify({
            "success": False,
            "message": "Failed to insert Arthakosha CSV records",
            "error": str(e)
        }), 500
