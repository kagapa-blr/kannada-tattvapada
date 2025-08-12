from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint,Float
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
    samputa_sankhye = Column(String(15), nullable=True)
    tatvapadakosha_sheershike = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)
    tatvapada_author_id = Column(Integer, ForeignKey("tatvapada_author_info.id"), nullable=False)
    tatvapadakarara_hesaru = relationship(
        TatvapadaAuthorInfo, backref="tatvapadagalu"
    )
    vibhag = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)
    tatvapada_sheershike = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)
    tatvapada_sankhye = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)
    tatvapada_first_line = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=True)
    tatvapada = Column(Text(collation='utf8mb4_unicode_ci'), nullable=True)

    # Explanation / commentary
    bhavanuvada = Column(Text(collation='utf8mb4_unicode_ci'), nullable=True)
    klishta_padagalu_artha = Column(Text(collation='utf8mb4_unicode_ci'), nullable=True)
    tippani = Column(Text(collation='utf8mb4_unicode_ci'), nullable=True)
