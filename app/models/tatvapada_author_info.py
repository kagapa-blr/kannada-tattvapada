from sqlalchemy import Column, Integer, String
from app.config.database import db_instance


class TatvapadaAuthorInfo(db_instance.Model):
    """
    Stores Tatvapadakara (author) information with Integer ID.
    """
    __tablename__ = "tatvapada_author_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hesaru = Column(String(255), unique=True, nullable=False)
