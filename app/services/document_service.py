# app/services/document_service.py
from app.config.database import db_instance
from app.models.documents import KannadaDocument
from sqlalchemy.exc import SQLAlchemyError


class ServiceResponse:
    """Standardized service response"""
    def __init__(self, success: bool, data=None, message: str = "", error: str = ""):
        self.success = success
        self.data = data
        self.message = message
        self.error = error

    def to_dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "error": self.error,
        }


class DocumentService:
    """Service layer for KannadaDocument CRUD"""

    @staticmethod
    def create_document(title, description, category, content):
        try:
            doc = KannadaDocument(
                title=title,
                description=description,
                category=category,
                content=content
            )
            db_instance.session.add(doc)
            db_instance.session.commit()
            return ServiceResponse(
                success=True,
                data={"id": doc.id},
                message="Document created successfully"
            )
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            return ServiceResponse(
                success=False,
                error=str(e.__cause__ or e),
                message="Failed to create document"
            )

    @staticmethod
    def get_all_documents():
        try:
            docs = KannadaDocument.query.order_by(KannadaDocument.created_at.desc()).all()
            data = [
                {
                    "id": d.id,
                    "title": d.title,
                    "description": d.description,
                    "category": d.category,
                    "created_at": d.created_at.isoformat(),
                    "updated_at": d.updated_at.isoformat()
                }
                for d in docs
            ]
            return ServiceResponse(success=True, data=data)
        except SQLAlchemyError as e:
            return ServiceResponse(
                success=False,
                error=str(e.__cause__ or e),
                message="Failed to fetch documents"
            )

    @staticmethod
    def get_document_by_id(doc_id):
        try:
            doc = KannadaDocument.query.get(doc_id)
            if not doc:
                return ServiceResponse(success=False, message="Document not found")
            return ServiceResponse(
                success=True,
                data={
                    "id": doc.id,
                    "title": doc.title,
                    "description": doc.description,
                    "category": doc.category,
                    "content": doc.content,
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat()
                }
            )
        except SQLAlchemyError as e:
            return ServiceResponse(success=False, error=str(e.__cause__ or e), message="Failed to fetch document")

    @staticmethod
    def update_document(doc_id, **kwargs):
        try:
            doc = KannadaDocument.query.get(doc_id)
            if not doc:
                return ServiceResponse(success=False, message="Document not found")

            for key, value in kwargs.items():
                if hasattr(doc, key) and value is not None:
                    setattr(doc, key, value)

            db_instance.session.commit()
            return ServiceResponse(success=True, message="Document updated successfully")
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            return ServiceResponse(success=False, error=str(e.__cause__ or e), message="Failed to update document")

    @staticmethod
    def delete_document(doc_id):
        try:
            doc = KannadaDocument.query.get(doc_id)
            if not doc:
                return ServiceResponse(success=False, message="Document not found")

            db_instance.session.delete(doc)
            db_instance.session.commit()
            return ServiceResponse(success=True, message="Document deleted successfully")
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            return ServiceResponse(success=False, error=str(e.__cause__ or e), message="Failed to delete document")
