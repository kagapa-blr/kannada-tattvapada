from flask import Blueprint, request, jsonify
from app.services.right_section import RightSection

# Blueprint with url_prefix for API versioning
right_section_impl_bp = Blueprint("right_section_impl", __name__, url_prefix="/api/v1/right-section")

# Service instance
right_section = RightSection()


# ----------------- Tatvapada Routes ----------------- #
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

    data = right_section.get_tatvapada_suchi(offset=offset, limit=limit, search=search)

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

    record = right_section.get_tatvapada_details(
        samputa_sankhye=samputa,
        tatvapada_author_id=author_id,
        tatvapada_sankhye=number,
    )

    if not record:
        return jsonify({"error": "Tatvapada not found"}), 404

    return jsonify(record)



# ----------------- Tippani Routes ----------------- #
@right_section_impl_bp.route("/all/tippani", methods=["GET"])
def get_tippanis():
    """
    GET /api/v1/right-section/tippani?offset=0&limit=10&search=
    Returns: samputa_sankhye, author id, author name, tippani, tippani id
    """
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 10))
    search = request.args.get("search", "")

    results = right_section.get_tippanis(offset=offset, limit=limit, search=search)

    if not results["results"]:
        return jsonify({"error": "No Tippanis found"}), 404

    return jsonify(results)


# 1. Get Samputa → Authors
@right_section_impl_bp.route("/samputa-authors", methods=["GET"])
def get_samputa_authors():
    try:
        data = right_section.get_samputa_with_authors()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# 2. Get Tippani by Samputa + Author
@right_section_impl_bp.route("/tippani", methods=["GET"])
def get_tippani():
    samputa = request.args.get("samputa")
    author_id = request.args.get("author_id", type=int)

    if not samputa or not author_id:
        return jsonify({"success": False, "message": "samputa and author_id required"}), 400

    data = right_section.get_tippani_by_samputa_author(samputa, author_id)
    return jsonify({"success": True, "data": data})  # data can be None if not found


# 3. Create Tippani
@right_section_impl_bp.route("/tippani", methods=["POST"])
def create_tippani():
    body = request.json
    samputa = body.get("samputa")
    author_id = body.get("author_id")
    content = body.get("content")

    try:
        # Create new Tippani
        data = right_section.create_tippani(samputa, author_id, content)
        return jsonify({"success": True, "data": data})
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# 4. Update Tippani by ID
@right_section_impl_bp.route("/tippani/<int:tippani_id>", methods=["PUT"])
def update_tippani(tippani_id):
    body = request.json
    content = body.get("content")

    if content is None:
        return jsonify({"success": False, "message": "content required"}), 400

    data = right_section.update_tippani(tippani_id, content)
    if data:
        return jsonify({"success": True, "data": data})
    return jsonify({"success": False, "message": "Tippani not found"}), 404


# 5. Delete Tippani by Samputa + Author
@right_section_impl_bp.route("/tippani", methods=["DELETE"])
def delete_tippani():
    body = request.json
    samputa = body.get("samputa")
    author_id = body.get("author_id")

    if not samputa or not author_id:
        return jsonify({"success": False, "message": "samputa and author_id required"}), 400

    deleted = right_section.delete_tippani(samputa, author_id)
    if deleted:
        return jsonify({"success": True, "message": "Tippani deleted successfully"})
    return jsonify({"success": False, "message": "Tippani not found"}), 404
