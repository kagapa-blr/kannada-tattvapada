from flask import Blueprint, request, jsonify

from app.services.right_section import TatvapadakararaVivaraService
from app.utils.auth_decorator import admin_required

tatvapadakarara_bp = Blueprint("tatvapadakarara", __name__, url_prefix="/api/v1")

# ---------------------------
# CREATE
# ---------------------------
@tatvapadakarara_bp.route("/authors", methods=["POST"])
@admin_required
def create_author():
    data = request.get_json()
    if not data or "author_name" not in data or "content" not in data:
        return jsonify({"error": "author_name and content are required"}), 400

    author, error = TatvapadakararaVivaraService.create_author(
        author_name=data["author_name"],
        content=data["content"]
    )

    if error:
        return jsonify({"error": error}), 409

    return jsonify({
        "message": "Author created successfully",
        "author": {
            "id": author.id,
            "author_name": author.author_name,
            "content": author.content
        }
    }), 201


# ---------------------------
# READ ALL
# ---------------------------
@tatvapadakarara_bp.route("/authors", methods=["GET"])
def get_authors():
    authors = TatvapadakararaVivaraService.get_all_authors()
    return jsonify({
        "data": [
            {
                "id": a.id,
                "author_name": a.author_name,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "updated_at": a.updated_at.isoformat() if a.updated_at else None,
            }
            for a in authors
        ]
    }), 200


# ---------------------------
# READ SINGLE
# ---------------------------
@tatvapadakarara_bp.route("/authors/<int:author_id>", methods=["GET"])
def get_author(author_id):
    author = TatvapadakararaVivaraService.get_author_by_id(author_id)
    if not author:
        return jsonify({"error": "Author not found"}), 404

    return jsonify({
        "id": author.id,
        "author_name": author.author_name,
        "content": author.content,
        "created_at": author.created_at,
        "updated_at": author.updated_at
    }), 200


# ---------------------------
# UPDATE
# ---------------------------
@tatvapadakarara_bp.route("/authors/<int:author_id>", methods=["PUT"])
@admin_required
def update_author(author_id):
    data = request.get_json()
    author, error = TatvapadakararaVivaraService.update_author(
        author_id,
        author_name=data.get("author_name"),
        content=data.get("content")
    )

    if error:
        return jsonify({"error": error}), 404

    return jsonify({
        "message": "Author updated successfully",
        "author": {
            "id": author.id,
            "author_name": author.author_name,
            "content": author.content
        }
    }), 200


# ---------------------------
# DELETE
# ---------------------------
@tatvapadakarara_bp.route("/authors/<int:author_id>", methods=["DELETE"])
@admin_required
def delete_author(author_id):
    success, error = TatvapadakararaVivaraService.delete_author(author_id)
    if not success:
        return jsonify({"error": error}), 404

    return jsonify({"message": "Author deleted successfully"}), 200
