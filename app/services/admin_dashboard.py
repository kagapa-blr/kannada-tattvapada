from sqlalchemy import func
from app.config.database import db_instance
from app.models.documents import TatvapadakararaVivara, KannadaDocument
from app.models.tatvapada import Tatvapada, ParibhashikaPadavivarana, Arthakosha
from app.models.tatvapada_author_info import TatvapadaAuthorInfo
from app.models.user_management import Admin
from app.utils.logger import setup_logger


class DashboardService:
    def __init__(self):
        self.logger = setup_logger(name="dashboard", log_file="dashboard")

    def get_overview_statistics(self) -> dict:
        try:
            # --- Tatvapada ---
            total_samputa = db_instance.session.query(
                func.count(func.distinct(Tatvapada.samputa_sankhye))
            ).scalar()
            total_tatvapada = db_instance.session.query(func.count(Tatvapada.id)).scalar()
            total_authors = db_instance.session.query(func.count(TatvapadaAuthorInfo.id)).scalar()

            tatvapada_per_samputa = (
                db_instance.session.query(
                    Tatvapada.samputa_sankhye,
                    func.count(Tatvapada.id).label("total_tatvapada"),
                    func.count(func.distinct(Tatvapada.tatvapada_author_id)).label("total_authors")
                )
                .group_by(Tatvapada.samputa_sankhye)
                .all()
            )
            tatvapada_per_samputa_list = [
                {"samputa_sankhye": s or "Unknown", "total_tatvapada": t, "total_authors": a}
                for s, t, a in tatvapada_per_samputa
            ]

            # --- Paribhashika ---
            total_paribhashika = db_instance.session.query(
                func.count(ParibhashikaPadavivarana.paribhashika_padavivarana_id)
            ).scalar()
            paribhashika_per_samputa = (
                db_instance.session.query(
                    ParibhashikaPadavivarana.samputa_sankhye,
                    func.count(ParibhashikaPadavivarana.paribhashika_padavivarana_id).label("count")
                )
                .group_by(ParibhashikaPadavivarana.samputa_sankhye)
                .all()
            )
            paribhashika_per_samputa_list = [
                {"samputa_sankhye": s or "Unknown", "count": c} for s, c in paribhashika_per_samputa
            ]

            # --- Arthakosha ---
            total_arthakosha = db_instance.session.query(func.count(Arthakosha.id)).scalar()
            arthakosha_per_samputa = (
                db_instance.session.query(
                    Arthakosha.samputa,
                    func.count(Arthakosha.id).label("count")
                )
                .group_by(Arthakosha.samputa)
                .all()
            )
            arthakosha_per_samputa_list = [
                {"samputa_sankhye": s or "Unknown", "count": c} for s, c in arthakosha_per_samputa
            ]

            # --- KannadaDocument ---
            total_documents = db_instance.session.query(func.count(KannadaDocument.id)).scalar()

            # --- TatvapadakararaVivara ---
            total_author_vivaras = db_instance.session.query(func.count(TatvapadakararaVivara.id)).scalar()
            tatvapadakarara_vivara_list = (
                db_instance.session.query(TatvapadakararaVivara.id, TatvapadakararaVivara.author_name)
                .order_by(TatvapadakararaVivara.id)
                .all()
            )
            tatvapadakarara_vivara_list = [
                {"id": i, "author_name": n} for i, n in tatvapadakarara_vivara_list
            ]

            # --- Admin Users ---
            total_admins = db_instance.session.query(func.count(Admin.id)).scalar()

            return {
                "success": True,
                "data": {
                    # Count Cards
                    "total_samputa": total_samputa,
                    "total_tatvapada": total_tatvapada,
                    "total_authors": total_authors,
                    "total_admins": total_admins,
                    "total_paribhashika": total_paribhashika,
                    "total_arthakosha": total_arthakosha,
                    "total_documents": total_documents,
                    "total_author_vivaras": total_author_vivaras,

                    # Tables
                    "tatvapada_per_samputa": tatvapada_per_samputa_list,
                    "paribhashika_per_samputa": paribhashika_per_samputa_list,
                    "arthakosha_per_samputa": arthakosha_per_samputa_list,
                    "tatvapadakarara_vivara_list": tatvapadakarara_vivara_list
                }
            }

        except Exception as e:
            error_message = f"Error fetching dashboard stats: {str(e)}"
            if self.logger:
                self.logger.error(error_message)
            # Return structured error for frontend
            return {
                "success": False,
                "error": error_message
            }
