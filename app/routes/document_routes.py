from flask import Blueprint, request, jsonify
from werkzeug.exceptions import NotFound, BadRequest

from app.services.document_service import (create_document,
                                           get_all_documents,
                                           get_document_by_id,
                                           update_document,
                                           delete_document)

documents_bp = Blueprint("kannada_documents", __name__, url_prefix="/api/documents")


# ---------------- CREATE ----------------
@documents_bp.route("", methods=["POST"])
def create_doc():
    data = request.get_json()
    if not data or "title" not in data or "content" not in data:
        raise BadRequest("Title and Content are required")

    doc = create_document(
        title=data["title"],
        description=data.get("description"),
        category=data.get("category"),
        content=data["content"]
    )

    return jsonify({"id": doc.id, "message": "Document created successfully"}), 201


# ---------------- READ (All) ----------------
@documents_bp.route("/", methods=["GET"])
def list_docs():
    docs = get_all_documents()
    return jsonify([
        {
            "id": d.id,
            "title": d.title,
            "description": d.description,
            "category": d.category,
            "content": d.content,
            "created_at": d.created_at.isoformat(),
            "updated_at": d.updated_at.isoformat()
        }
        for d in docs
    ])


# ---------------- READ (Single) ----------------
@documents_bp.route("/<int:doc_id>", methods=["GET"])
def get_doc(doc_id):
    doc = get_document_by_id(doc_id)
    if not doc:
        raise NotFound("Document not found")
    return jsonify({
        "id": doc.id,
        "title": doc.title,
        "description": doc.description,
        "category": doc.category,
        "content": doc.content,
        "created_at": doc.created_at.isoformat(),
        "updated_at": doc.updated_at.isoformat()
    })


# ---------------- UPDATE ----------------
@documents_bp.route("/<int:doc_id>", methods=["PUT"])
def update_doc(doc_id):
    data = request.get_json()
    doc = update_document(doc_id, **data)
    if not doc:
        raise NotFound("Document not found")
    return jsonify({"message": "Document updated successfully"})


# ---------------- DELETE ----------------
@documents_bp.route("/<int:doc_id>", methods=["DELETE"])
def delete_doc(doc_id):
    success = delete_document(doc_id)
    if not success:
        raise NotFound("Document not found")
    return jsonify({"message": "Document deleted successfully"})
