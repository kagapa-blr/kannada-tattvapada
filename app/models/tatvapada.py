from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.config.database import db_instance
from app.models.tatvapada_author_info import TatvapadaAuthorInfo


class Tatvapada(db_instance.Model):
    """
    Tatvapada entry with UUID-based author reference.
    """
    __tablename__ = "tatvapada"
    __table_args__ = (
        UniqueConstraint(
            'samputa_sankhye',
            'tatvapada_sankhye',
            'tatvapada_author_id',
            name='uq_tatvapada_composite'
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identifiers and metadata
    tatvapadakosha = Column(String(255), nullable=False)
    samputa_sankhye = Column(Integer, nullable=True)
    tatvapadakosha_sheershike = Column(String(255), nullable=True)
    mukhya_sheershike = Column(String(255), nullable=True)

    tatvapada_author_id = Column(Integer, ForeignKey("tatvapada_author_info.id"), nullable=False)
    tatvapadakarara_hesaru = relationship(TatvapadaAuthorInfo, backref="tatvapadagalu")

    # Verse information
    tatvapada_sankhye = Column(String(255), nullable=True)
    tatvapada_hesaru = Column(String(255), nullable=True)
    tatvapada = Column(Text, nullable=True)

    # Explanation
    klishta_padagalu_artha = Column(Text, nullable=True)
    tippani = Column(Text, nullable=True)
