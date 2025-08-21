from flask import Blueprint, request, jsonify, render_template
from app.services.right_section import RightSection

# Blueprint with url_prefix for API versioning
right_section_impl_bp = Blueprint(
    "right_section_impl", __name__, url_prefix="/api/v1/right-section"
)

# Service instance
right_section = RightSection()


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

    data = right_section.get_tatvapada_list(offset=offset, limit=limit, search=search)

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
    Fetches a particular tatvapada entry.
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

    # record is already a dict from service layer
    return jsonify(record)

