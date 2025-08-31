from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.config.database import db_instance
from app.models.tatvapada_author_info import TatvapadaAuthorInfo


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
    """
    ಅರ್ಥಕೋಶ (Arthakosha) table for storing Kannada glossary words and meanings.
    Linked to TatvapadaAuthorInfo for author metadata.
    """
    __tablename__ = "arthakosha"
    __table_args__ = (
        UniqueConstraint('samputa', 'author_id', 'id', name='uq_arthakosha_per_author_per_samputa'),
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
    title = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)  # New title column
    word = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    meaning = Column(Text(collation='utf8mb4_unicode_ci'), nullable=False)
    notes = Column(Text(collation='utf8mb4_unicode_ci'), nullable=True)
