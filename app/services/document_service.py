from app.config.database import db_instance
from app.models.documents import KannadaDocument


def create_document(title, description, category, content):
    """Create a new Kannada document"""
    doc = KannadaDocument(
        title=title,
        description=description,
        category=category,
        content=content
    )
    db_instance.session.add(doc)
    db_instance.session.commit()
    return doc


def get_all_documents():
    """Fetch all documents"""
    return KannadaDocument.query.order_by(KannadaDocument.created_at.desc()).all()


def get_document_by_id(doc_id):
    """Fetch a single document by ID"""
    return KannadaDocument.query.get(doc_id)


def update_document(doc_id, **kwargs):
    """Update an existing document"""
    doc = KannadaDocument.query.get(doc_id)
    if not doc:
        return None

    for key, value in kwargs.items():
        if hasattr(doc, key) and value is not None:
            setattr(doc, key, value)

    db_instance.session.commit()
    return doc


def delete_document(doc_id):
    """Delete a document"""
    doc = KannadaDocument.query.get(doc_id)
    if not doc:
        return False

    db_instance.session.delete(doc)
    db_instance.session.commit()
    return True
