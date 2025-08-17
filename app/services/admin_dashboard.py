from sqlalchemy import func

from app.config.database import db_instance
from app.models.tatvapada import Tatvapada
from app.models.tatvapada_author_info import TatvapadaAuthorInfo
from app.models.user_management import Admin
from app.utils.logger import setup_logger


class DashboardService:
    def __init__(self):
        self.logger = setup_logger(name='dashboard',log_file='dashboard')

    def get_overview_statistics(self) -> dict:
        try:
            # Total number of distinct Samputa
            total_samputa = db_instance.session.query(
                func.count(func.distinct(Tatvapada.samputa_sankhye))
            ).scalar()

            # Total Tatvapada entries
            total_tatvapada = db_instance.session.query(
                func.count(Tatvapada.id)
            ).scalar()

            # Total Authors
            total_authors = db_instance.session.query(
                func.count(TatvapadaAuthorInfo.id)
            ).scalar()

            # Number of Tatvapada in each Samputa
            tatvapada_per_samputa = (
                db_instance.session.query(
                    Tatvapada.samputa_sankhye,
                    func.count(Tatvapada.id).label("count")
                )
                .group_by(Tatvapada.samputa_sankhye)
                .all()
            )
            tatvapada_per_samputa_list = [
                {"samputa_sankhye": s or "Unknown", "count": c}
                for s, c in tatvapada_per_samputa
            ]

            # Total Admin Users
            total_admins = db_instance.session.query(
                func.count(Admin.id)
            ).scalar()

            return {
                "total_samputa": total_samputa,
                "total_tatvapada": total_tatvapada,
                "total_authors": total_authors,
                "tatvapada_per_samputa": tatvapada_per_samputa_list,
                "total_admins": total_admins
            }

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error fetching dashboard stats: {e}")
            raise
