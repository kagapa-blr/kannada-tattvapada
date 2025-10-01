# from sqlalchemy import Column, Integer, String
# from app.config.database import db_instance
#
# class TatvapadaAuthorInfo(db_instance.Model):
#     """
#     Stores Tatvapadakara (author) information with Integer ID.
#     Supports Unicode (Kannada).
#     """
#     __tablename__ = "tatvapada_author_info"
#     __table_args__ = {
#         'mysql_engine': 'InnoDB',
#         'mysql_charset': 'utf8mb4',
#         'mysql_collate': 'utf8mb4_unicode_ci'
#     }
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     tatvapadakarara_hesaru = Column(String(255, collation='utf8mb4_unicode_ci'), unique=True, nullable=False)
