"""
Tatvapada model definition.

Defines the SQLAlchemy model for storing 'Tatvapada' entries, which are components of a
philosophical or linguistic corpus. Each entry includes metadata such as chapter numbers,
titles, author names, and content.
"""

from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from app.config.database import db_instance


class Tatvapada(db_instance.Model):
    """
    Represents a single Tatvapada (philosophical verse or term) record.

    Enforced Constraint:
    - The combination of 'tatvapadakosha_sankhye', 'samputa_sankhye',
      and 'tatvapada_sankhye' must be unique.
    """

    __tablename__ = "tatvapada"
    __table_args__ = (
        UniqueConstraint(
            'tatvapadakosha_sankhye',
            'samputa_sankhye',
            'tatvapada_sankhye',
            name='uq_tatvapada_composite'
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identifiers and metadata
    tatvapadakosha = Column(String(255), nullable=False)
    tatvapadakosha_sankhye = Column(Integer, nullable=False)
    samputa_sankhye = Column(Integer, nullable=True)
    tatvapadakosha_sheershike = Column(String(255), nullable=True)
    tatvapadakarara_hesaru = Column(String(255), nullable=True)
    mukhya_sheershike = Column(String(255), nullable=True)

    # Verse information
    tatvapada_sankhye = Column(String(255), nullable=True)
    tatvapada_hesaru = Column(String(255), nullable=True)
    tatvapada = Column(Text, nullable=True)

    # Explanation
    klishta_padagalu_artha = Column(Text, nullable=True)
    tippani = Column(Text, nullable=True)
