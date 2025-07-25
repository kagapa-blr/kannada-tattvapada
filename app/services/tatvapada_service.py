from typing import Optional, List, Dict
from sqlalchemy.exc import SQLAlchemyError
from app.models.tatvapada import Tatvapada
from app.config.database import db_instance
from app.utils.logger import setup_logger


class TatvapadaService:
    """
    Service class to manage CRUD operations and queries for Tatvapada model.
    """

    def __init__(self):
        self.logger = setup_logger("tatvapada_service", "tatvapada_service.log")

    def insert_tatvapada(self, data: dict) -> Optional[Tatvapada]:
        try:
            new_entry = Tatvapada(**data)
            db_instance.session.add(new_entry)
            db_instance.session.commit()
            self.logger.info(f"Inserted Tatvapada: {new_entry.tatvapada_hesaru}")
            return new_entry
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            self.logger.error(f"Error inserting Tatvapada: {e}")
            return None

    def search_by_keyword(self, keyword: str) -> List[Tatvapada]:
        try:
            results = Tatvapada.query.filter(
                Tatvapada.tatvapada.ilike(f"%{keyword}%")
            ).all()
            self.logger.info(f"Found {len(results)} entries containing keyword='{keyword}'")
            return results
        except SQLAlchemyError as e:
            self.logger.error(f"Error searching Tatvapada by keyword '{keyword}': {e}")
            return []

    def get_by_composite_keys(
        self,
        tatvapadakosha_sankhye: int,
        samputa_sankhye: int,
        tatvapada_sankhye: str
    ) -> Optional[Tatvapada]:
        try:
            return Tatvapada.query.filter_by(
                tatvapadakosha_sankhye=tatvapadakosha_sankhye,
                samputa_sankhye=samputa_sankhye,
                tatvapada_sankhye=tatvapada_sankhye
            ).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching by composite keys: {e}")
            return None

    def delete_tatvapada_by_composite_keys(
        self,
        tatvapadakosha_sankhye: int,
        samputa_sankhye: int,
        tatvapada_sankhye: str
    ) -> bool:
        try:
            record = self.get_by_composite_keys(
                tatvapadakosha_sankhye, samputa_sankhye, tatvapada_sankhye
            )
            if not record:
                self.logger.warning(
                    f"No record found for deletion: sankhye={tatvapada_sankhye}"
                )
                return False

            db_instance.session.delete(record)
            db_instance.session.commit()
            self.logger.info(f"Deleted Tatvapada: {tatvapada_sankhye}")
            return True
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            self.logger.error(f"Delete operation failed: {e}")
            return False

    def exists_by_tatvapadakosha(self, tatvapadakosha: str) -> bool:
        try:
            return db_instance.session.query(
                db_instance.session.query(Tatvapada)
                .filter_by(tatvapadakosha=tatvapadakosha)
                .exists()
            ).scalar()
        except SQLAlchemyError as e:
            self.logger.error(f"Exists check failed for '{tatvapadakosha}': {e}")
            return False

    def get_all_tatvapadakosha_mapping(self) -> Dict[int, str]:
        try:
            results = Tatvapada.query.with_entities(
                Tatvapada.tatvapadakosha_sankhye,
                Tatvapada.tatvapadakosha
            ).distinct().all()
            return {sankhye: name for sankhye, name in results}
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching tatvapadakosha mapping: {e}")
            return {}

    def get_samputa_by_tatvapadakosha(self, tatvapadakosha: str) -> List[int]:
        try:
            results = Tatvapada.query.filter_by(
                tatvapadakosha=tatvapadakosha
            ).with_entities(Tatvapada.samputa_sankhye).distinct().all()
            return [row[0] for row in results if row[0] is not None]
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching samputa by tatvapadakosha '{tatvapadakosha}': {e}")
            return []

    def get_tatvapada_sankhye_by_samputa(self, samputa_sankhye: int) -> List[str]:
        try:
            results = Tatvapada.query.filter_by(
                samputa_sankhye=samputa_sankhye
            ).with_entities(Tatvapada.tatvapada_sankhye).distinct().all()
            return [row[0] for row in results if row[0]]
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching tatvapada_sankhye by samputa {samputa_sankhye}: {e}")
            return []

    def get_tatvapada_by_sankhye(self, tatvapada_sankhye: str) -> Optional[Tatvapada]:
        try:
            return Tatvapada.query.filter_by(
                tatvapada_sankhye=tatvapada_sankhye
            ).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching Tatvapada by sankhye '{tatvapada_sankhye}': {e}")
            return None
