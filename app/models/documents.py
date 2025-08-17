from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime, timezone, timedelta
from app.config.database import db_instance

# Define IST timezone
IST = timezone(timedelta(hours=5, minutes=30))

def current_ist_time():
    """Returns current IST datetime with timezone info."""
    return datetime.now(IST)

class KannadaDocument(db_instance.Model):
    """
    Stores Kannada documents (full text) with metadata.
    Supports UTF-8 content and uses InnoDB engine.
    """
    __tablename__ = "sampadakar_documents"
    __table_args__ = (
        UniqueConstraint('title', name='uq_document_title'),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci'
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Document metadata
    title = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    description = Column(Text(collation='utf8mb4_unicode_ci'), nullable=True)
    category = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)

    # Content (Kannada text or HTML)
    content = Column(LONGTEXT(collation='utf8mb4_unicode_ci'), nullable=False)  # <-- changed to LONGTEXT

    # Timestamps (IST)
    created_at = Column(DateTime(timezone=True), default=current_ist_time)
    updated_at = Column(DateTime(timezone=True), default=current_ist_time, onupdate=current_ist_time)

    def __repr__(self):
        return f"<KannadaDocument(title='{self.title}', id={self.id})>"
