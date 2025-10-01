import hashlib
from datetime import datetime

import pytz
from sqlalchemy import Column, String, Text, Integer, Numeric, DateTime
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.config.database import db_instance

IST = pytz.timezone('Asia/Kolkata')


def ist_now():
    return datetime.now(IST)

class TatvapadaAuthorInfo(db_instance.Model):
    """
    Stores Tatvapadakara (author) information with Integer ID.
    Supports Unicode (Kannada).
    """
    __tablename__ = "tatvapada_author_info"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    tatvapadakarara_hesaru = Column(String(255, collation='utf8mb4_unicode_ci'), unique=True, nullable=False)


class Tatvapada(db_instance.Model):
    """
    Tatvapada entry with author reference.
    Supports Kannada Unicode and uses InnoDB engine.
    """
    __tablename__ = "tatvapada"
    __table_args__ = (
        UniqueConstraint(
            'samputa_sankhye',
            'tatvapada_sankhye',
            'tatvapada_author_id',
            name='uq_tatvapada_composite'
        ),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci'
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identifiers and metadata
    samputa_sankhye = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    tatvapadakosha_sheershike = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)
    tatvapada_author_id = Column(Integer, ForeignKey("tatvapada_author_info.id"), nullable=False)
    tatvapadakarara_hesaru = relationship(
        TatvapadaAuthorInfo, backref="tatvapadagalu"
    )
    vibhag = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)
    tatvapada_sheershike = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)
    tatvapada_sankhye = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    tatvapada_first_line = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)
    tatvapada = Column(Text(collation='utf8mb4_unicode_ci'), nullable=True)

    # Explanation / commentary
    bhavanuvada = Column(Text(collation='utf8mb4_unicode_ci'), nullable=True)
    klishta_padagalu_artha = Column(Text(collation='utf8mb4_unicode_ci'), nullable=True)
    tippani = Column(Text(collation='utf8mb4_unicode_ci'), nullable=True)

class ParibhashikaPadavivarana(db_instance.Model):
    __tablename__ = "paribhashika_padavivarana"

    paribhashika_padavivarana_id = Column(Integer, primary_key=True, autoincrement=True)
    tatvapada_author_id = Column(Integer, ForeignKey("tatvapada_author_info.id"), nullable=False)
    samputa_sankhye = Column(String(255), nullable=False)

    # Title (not globally unique)
    paribhashika_padavivarana_title = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)

    # Large content field
    paribhashika_padavivarana_content = Column(Text(collation='utf8mb4_unicode_ci'), nullable=False)

    author = relationship("TatvapadaAuthorInfo", backref="paribhashika_padavivaranagalu")

    __table_args__ = (
        UniqueConstraint('tatvapada_author_id', 'paribhashika_padavivarana_title', name='uq_author_title'),
    )

class Arthakosha(db_instance.Model):
    __tablename__ = "arthakosha"
    __table_args__ = (
        UniqueConstraint('author_id', 'word', 'meaning_hash', name='uq_arthakosha_author_word_meaning'),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci'
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    samputa = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    author_id = Column(Integer, ForeignKey("tatvapada_author_info.id"), nullable=False)
    author = relationship(TatvapadaAuthorInfo, backref="arthakoshas")
    title = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    word = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    meaning = Column(Text(collation='utf8mb4_unicode_ci'), nullable=False)
    meaning_hash = Column(String(64), nullable=False)  # SHA256 hash
    notes = Column(Text(collation='utf8mb4_unicode_ci'), nullable=True)

    def set_meaning(self, meaning_text):
        self.meaning = meaning_text
        self.meaning_hash = hashlib.sha256(meaning_text.encode('utf-8')).hexdigest()

class ShoppingTatvapada(db_instance.Model):
    __tablename__ = "shopping_tatvapada"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Reference to Author
    tatvapada_author_id = Column(Integer, ForeignKey("tatvapada_author_info.id"), nullable=False)
    author = relationship(TatvapadaAuthorInfo, backref="shopping_books")

    # Selling details
    samputa_sankhye = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    # Optional metadata for display
    tatvapadakosha_sheershike = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)

    def __init__(self, tatvapada_author_id: int, samputa_sankhye: str, price: float,
                 tatvapadakosha_sheershike: str = None):
        self.tatvapada_author_id = tatvapada_author_id
        self.samputa_sankhye = samputa_sankhye
        self.price = price
        self.tatvapadakosha_sheershike = tatvapadakosha_sheershike


class ShoppingBooks(db_instance.Model):
    """
    General-purpose Book model for selling books.
    Standalone version with IST timestamps, meaningful field names, and page count.
    """
    __tablename__ = "shopping_books"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Core book details
    title = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    subtitle = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)
    author_name = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)
    description = Column(Text(collation='utf8mb4_unicode_ci'), nullable=True)

    # Book identification
    book_code = Column(String(50, collation='utf8mb4_unicode_ci'), unique=True, nullable=True)
    catalog_number = Column(String(50, collation='utf8mb4_unicode_ci'), nullable=True)

    # Publishing details
    publisher_name = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)
    publication_date = Column(DateTime, nullable=True)
    number_of_pages = Column(Integer, nullable=True)  # New field added

    # Pricing & inventory
    price = Column(Numeric(10, 2), nullable=False)
    discount_price = Column(Numeric(10, 2), nullable=True)
    stock_quantity = Column(Integer, nullable=False, default=0)

    # Media
    cover_image_url = Column(String(500, collation='utf8mb4_unicode_ci'), nullable=True)

    # Metadata
    language = Column(String(50, collation='utf8mb4_unicode_ci'), nullable=True)
    created_at = Column(DateTime, default=ist_now)
    updated_at = Column(DateTime, default=ist_now, onupdate=ist_now)

    def __init__(self, title, price, **kwargs):
        self.title = title
        self.price = price
        for key, value in kwargs.items():
            setattr(self, key, value)
