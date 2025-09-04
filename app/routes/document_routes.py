from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest, NotFound
from app.services.document_service import DocumentService

documents_bp = Blueprint("kannada_documents", __name__, url_prefix="/api/documents")


# ---------------- CREATE ----------------
@documents_bp.route("/", methods=["POST"])
def create_doc():
    data = request.get_json(silent=True)
    if not data or "title" not in data or "content" not in data:
        return jsonify({"message": "Title and Content are required"}), 400

    result = DocumentService.create_document(
        title=data["title"],
        description=data.get("description"),
        category=data.get("category"),
        content=data["content"]
    )

    if not result.success:
        return jsonify({
            "message": result.message or "Failed to create document",
            "error": result.error
        }), 400

    return jsonify({
        "id": result.data["id"],
        "message": result.message
    }), 201


# ---------------- READ (All) ----------------
@documents_bp.route("/", methods=["GET"])
def list_docs():
    result = DocumentService.get_all_documents()
    if not result.success:
        return jsonify({"message": result.message, "error": result.error}), 500

    return jsonify(result.data), 200


# ---------------- READ (Single) ----------------
@documents_bp.route("/<int:doc_id>", methods=["GET"])
def get_doc(doc_id):
    result = DocumentService.get_document_by_id(doc_id)
    if not result.success:
        raise NotFound(result.message or "Document not found")

    return jsonify(result.data), 200


# ---------------- UPDATE ----------------
@documents_bp.route("/<int:doc_id>", methods=["PUT"])
def update_doc(doc_id):
    data = request.get_json()
    result = DocumentService.update_document(doc_id, **data)

    if not result.success:
        if result.message == "Document not found":
            raise NotFound(result.message)
        raise BadRequest(result.message or "Failed to update document")

    return jsonify({"message": result.message}), 200


# ---------------- DELETE ----------------
@documents_bp.route("/<int:doc_id>", methods=["DELETE"])
def delete_doc(doc_id):
    result = DocumentService.delete_document(doc_id)

    if not result.success:
        raise NotFound(result.message or "Document not found")

    return jsonify({"message": result.message}), 200
