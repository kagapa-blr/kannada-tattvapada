from typing import List
from typing import Optional

from sqlalchemy import distinct
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.config.database import db_instance
from app.models.tatvapada import Tatvapada
from app.models.tatvapada_author_info import TatvapadaAuthorInfo
from app.utils.logger import setup_logger


class TatvapadaService:
    """
    Service class to manage CRUD operations and queries for Tatvapada model.
    """

    def __init__(self):
        self.logger = setup_logger("tatvapada_service", "tatvapada_service.log")

    def insert_tatvapada(self, data: dict) -> Optional[Tatvapada]:
        try:
            # Work on a shallow copy so caller's dict isn't mutated unexpectedly
            payload = data.copy()

            author_name = payload.pop("tatvapadakarara_hesaru", None)
            author_id = payload.get("tatvapada_author_id", None)

            # Case: both provided -> ensure consistency
            if author_name and author_id:
                existing_author = TatvapadaAuthorInfo.query.filter_by(id=author_id).first()
                if not existing_author:
                    raise ValueError(f"Provided tatvapada_author_id '{author_id}' does not exist")
                if existing_author.tatvapadakarara_hesaru != author_name:
                    raise ValueError(
                        "Conflict: provided tatvapadakarara_hesaru and tatvapada_author_id refer to different authors"
                    )
                author = existing_author

            # Case: only author name provided
            elif author_name:
                author = TatvapadaAuthorInfo.query.filter_by(tatvapadakarara_hesaru=author_name).first()
                if not author:
                    author = TatvapadaAuthorInfo(tatvapadakarara_hesaru=author_name)
                    db_instance.session.add(author)
                    db_instance.session.flush()  # generate UUID / ID

            # Case: only author ID provided
            elif author_id:
                author = TatvapadaAuthorInfo.query.filter_by(id=author_id).first()
                if not author:
                    raise ValueError(f"tatvapada_author_id '{author_id}' does not exist")
                author_name = author.tatvapadakarara_hesaru  # derive name if needed

            else:
                raise ValueError("Either tatvapadakarara_hesaru or tatvapada_author_id must be provided")

            # Ensure author is present and assign its ID
            payload["tatvapada_author_id"] = author.id

            # Create the Tatvapada entry
            new_entry = Tatvapada(**{k: v for k, v in payload.items() if k != "tatvapadakarara_hesaru"})
            db_instance.session.add(new_entry)
            db_instance.session.commit()

            self.logger.info(f"Inserted Tatvapada for author: {author.tatvapadakarara_hesaru}")
            return new_entry

        except Exception as e:
            db_instance.session.rollback()
            self.logger.error(f"Error inserting Tatvapada: {e}")
            raise


    def update_by_composite_keys(
            self,
            samputa_sankhye: float,
            tatvapada_sankhye: str,
            tatvapada_author_id: int,
            data: dict
    ) -> Optional[Tatvapada]:
        try:
            # Step 1: Fetch the existing entry
            existing_entry = Tatvapada.query.filter_by(
                samputa_sankhye=samputa_sankhye,
                tatvapada_sankhye=tatvapada_sankhye,
                tatvapada_author_id=tatvapada_author_id
            ).first()

            if not existing_entry:
                raise ValueError("Tatvapada entry not found with the given composite keys.")

            # Step 2: Make a safe copy of incoming data
            update_data = dict(data)

            # Step 3: Remove immutable fields from the update set
            immutable_fields = ["samputa_sankhye", "tatvapada_sankhye", "tatvapada_author_id"]
            for field in immutable_fields:
                if field in update_data:
                    self.logger.debug(f"Ignoring update to immutable field: {field}")
                    update_data.pop(field)

            # Step 4: If author name is provided, update the shared author record
            author_name = update_data.pop("tatvapadakarara_hesaru", None)
            if author_name and author_name.strip():
                if existing_entry.tatvapadakarara_hesaru:
                    existing_entry.tatvapadakarara_hesaru.tatvapadakarara_hesaru = author_name.strip()
                else:
                    raise ValueError("Author relationship missing; cannot update author name.")

            # Step 5: Update remaining allowed fields
            for key, value in update_data.items():
                if hasattr(existing_entry, key):
                    setattr(existing_entry, key, value)

            db_instance.session.commit()
            self.logger.info(
                f"Updated Tatvapada entry with keys: {samputa_sankhye}, {tatvapada_sankhye}, {tatvapada_author_id}"
            )
            return existing_entry

        except IntegrityError as e:
            db_instance.session.rollback()
            error_str = str(e.orig)

            # Handle duplicate author name case
            if "tatvapada_author_info.tatvapadakarara_hesaru" in error_str:
                self.logger.warning(f"Duplicate author name attempted: {error_str}")
                raise ValueError("The author name already exists. Please choose a different name.")

            # Handle any other unique constraint violations
            if "uq_tatvapada_composite" in error_str:
                self.logger.warning(f"Duplicate composite key attempted: {error_str}")
                raise ValueError("A Tatvapada entry with the same samputa, sankhye, and author already exists.")

            self.logger.error(f"Database integrity error: {error_str}")
            raise ValueError("A database constraint was violated. Please review your input.")

        except ValueError as ve:
            db_instance.session.rollback()
            self.logger.warning(f"Validation error: {ve}")
            raise ve

        except SQLAlchemyError as sqle:
            db_instance.session.rollback()
            self.logger.error(f"Unexpected database error: {sqle}")
            raise ValueError("An unexpected database error occurred while updating the Tatvapada.")

        except Exception as ex:
            db_instance.session.rollback()
            self.logger.error(f"Unexpected error: {ex}")
            raise ValueError("An unexpected error occurred while updating the Tatvapada.")

    def delete_tatvapada_by_samputa(self, samputa_sankhye: int) -> int:
        """
        Deletes all Tatvapada entries for a given samputa_sankhye.
        Returns the count of rows deleted.
        """
        try:
            deleted = Tatvapada.query.filter_by(samputa_sankhye=samputa_sankhye).delete()
            db_instance.session.commit()
            self.logger.info(f"Deleted {deleted} Tatvapada entries for samputa_sankhye={samputa_sankhye}")
            return deleted
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            self.logger.error(f"Error deleting Tatvapada by samputa_sankhye={samputa_sankhye}: {e}")
            raise

    def delete_specific_tatvapada(self, samputa_sankhye: int, tatvapada_author_id: int, tatvapada_sankhye: str) -> bool:
        """
        Deletes a specific Tatvapada entry identified by the composite key.
        Returns True if deletion was successful, False if no record matched.
        """
        try:
            entry = Tatvapada.query.filter_by(
                samputa_sankhye=samputa_sankhye,
                tatvapada_author_id=tatvapada_author_id,
                tatvapada_sankhye=tatvapada_sankhye
            ).first()

            if not entry:
                return False

            db_instance.session.delete(entry)
            db_instance.session.commit()
            self.logger.info(
                f"Deleted Tatvapada with samputa={samputa_sankhye}, author_id={tatvapada_author_id}, sankhye={tatvapada_sankhye}")
            return True
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            self.logger.error(f"Error deleting specific Tatvapada: {e}")
            raise

    def search_by_keyword(self, keyword: str) -> list:
        try:
            results = Tatvapada.query.filter(
                Tatvapada.tatvapada.ilike(f"%{keyword}%")
            ).all()
            self.logger.info(f"Found {len(results)} entries containing keyword='{keyword}'")
            return results
        except SQLAlchemyError as e:
            self.logger.error(f"Error searching Tatvapada by keyword '{keyword}': {e}")
            return []

    def get_all_samputa_sankhye(self) -> List[int]:
        """
        Returns a list of all distinct samputa_sankhye values (non-null).
        """
        try:
            results = Tatvapada.query.with_entities(
                distinct(Tatvapada.samputa_sankhye)
            ).all()
            return [row[0] for row in results if row[0] is not None]
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching all samputa_sankhye: {e}")
            return []

    def get_tatvapada_sankhye_by_samputa(self, samputa_sankhye: int) -> List[int]:
        """
        Returns a list of tatvapada_sankhye (as integers) for a given samputa_sankhye.
        """
        try:
            results = Tatvapada.query.filter_by(
                samputa_sankhye=samputa_sankhye
            ).with_entities(Tatvapada.tatvapada_sankhye).distinct().all()

            return [int(row[0]) for row in results if row[0] is not None]
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching tatvapada_sankhye by samputa {samputa_sankhye}: {e}")
            return []


    def get_authors_and_sankhyes_by_samputa(self, samputa_sankhye: int) -> List[dict]:
        """
        Returns a list of dicts with keys: 'tatvapadakarara_hesaru' and 'tatvapada_sankhye'
        for the given samputa_sankhye.
        """
        try:
            results = Tatvapada.query.filter_by(
                samputa_sankhye=samputa_sankhye
            ).with_entities(
                Tatvapada.tatvapadakarara_hesaru,
                Tatvapada.tatvapada_sankhye
            ).distinct().all()

            return [
                {
                    "tatvapadakarara_hesaru": row[0],
                    "tatvapada_sankhye": int(row[1]) if row[1] is not None else None
                }
                for row in results
                if row[0] is not None and row[1] is not None
            ]
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching authors and sankhyes by samputa {samputa_sankhye}: {e}")
            return []

    def get_sankhyes_with_author_by_samputa(self, samputa_sankhye: int) -> List[dict]:
        """
        Returns a list of dicts with tatvapada_sankhye, author id, and author name (hesaru)
        for a given samputa_sankhye.
        """
        try:
            results = (
                db_instance.session.query(
                    Tatvapada.tatvapada_sankhye,
                    TatvapadaAuthorInfo.id,
                    TatvapadaAuthorInfo.tatvapadakarara_hesaru
                )
                .join(
                    TatvapadaAuthorInfo,
                    Tatvapada.tatvapada_author_id == TatvapadaAuthorInfo.id
                )
                .filter(Tatvapada.samputa_sankhye == samputa_sankhye)
                .distinct()
                .all()
            )
            return [
                {
                    "tatvapada_sankhye": int(tps),
                    "tatvapadakarara_id": author_id,
                    "tatvapadakarara_hesaru": author_name
                }
                for tps, author_id, author_name in results if tps is not None
            ]
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching sankhyes with author for samputa {samputa_sankhye}: {e}")
            return []


    def get_specific_tatvapada(self, samputa_sankhye: int, tatvapada_author_id: int, tatvapada_sankhye: str) -> \
    Optional[Tatvapada]:
        """
        Fetches a specific Tatvapada entry based on the composite key:
        samputa_sankhye, tatvapada_author_id, and tatvapada_sankhye.

        Returns:
            Tatvapada object if found, else None.
        """
        try:
            return Tatvapada.query.filter_by(
                samputa_sankhye=samputa_sankhye,
                tatvapada_author_id=tatvapada_author_id,
                tatvapada_sankhye=tatvapada_sankhye
            ).first()
        except SQLAlchemyError as e:
            self.logger.error(
                f"Error fetching specific tatvapada (samputa: {samputa_sankhye}, "
                f"author_id: {tatvapada_author_id}, sankhye: {tatvapada_sankhye}): {e}"
            )
            return None

