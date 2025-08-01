from typing import List
from typing import Optional

from sqlalchemy import distinct
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

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



    def insert_tatvapada1(self, data: dict) -> Optional[Tatvapada]:
        try:
            new_entry = Tatvapada(**data)
            db_instance.session.add(new_entry)
            db_instance.session.commit()
            self.logger.info(f"Inserted Tatvapada: {new_entry.tatvapada_hesaru}")
            return new_entry
        except IntegrityError as ie:
            db_instance.session.rollback()
            self.logger.error(f"IntegrityError (possibly duplicate): {ie}")
            raise ie  # Propagate up to the route handler
        except SQLAlchemyError as e:
            db_instance.session.rollback()
            self.logger.error(f"General DB error while inserting Tatvapada: {e}")
            raise e  # Propagate up

    def insert_tatvapada(self, data: dict) -> Optional[Tatvapada]:
        try:
            # Step 1: Extract author name
            author_name = data.pop("tatvapadakarara_hesaru", None)
            if not author_name:
                raise ValueError("Author name (tatvapadakarara_hesaru) is required")

            # Step 2: Look up existing author
            author = TatvapadaAuthorInfo.query.filter_by(tatvapadakarara_hesaru=author_name).first()

            # Step 3: If not found, create author
            if not author:
                author = TatvapadaAuthorInfo(tatvapadakarara_hesaru=author_name)
                db_instance.session.add(author)
                db_instance.session.flush()  # To generate the UUID

            # Step 4: Assign author ID to the tatvapada
            data["tatvapada_author_id"] = author.id

            # Step 5: Create the Tatvapada object
            new_entry = Tatvapada(**data)
            db_instance.session.add(new_entry)
            db_instance.session.commit()

            self.logger.info(f"Inserted Tatvapada for author: {author_name}")
            return new_entry

        except Exception as e:
            db_instance.session.rollback()
            self.logger.error(f"Error inserting Tatvapada: {e}")
            raise e

    def update_tatvapada(self, entry_id: int, data: dict) -> Optional[Tatvapada]:
        try:
            # Step 1: Fetch existing entry
            existing_entry = Tatvapada.query.get(entry_id)
            if not existing_entry:
                raise ValueError(f"Tatvapada entry with id {entry_id} not found")

            # Step 2: Check for unique constraint violation attempt
            immutable_fields = {
                "samputa_sankhye": existing_entry.samputa_sankhye,
                "tatvapada_sankhye": existing_entry.tatvapada_sankhye,
                "tatvapada_author_id": existing_entry.tatvapada_author_id
            }

            # If author name is being passed for update, map it to ID first
            author_name = data.get("tatvapadakarara_hesaru")
            if author_name:
                existing_author = TatvapadaAuthorInfo.query.filter_by(tatvapadakarara_hesaru=author_name).first()
                if not existing_author:
                    raise ValueError(f"Author '{author_name}' not found. Please add the author before updating.")
                data["tatvapada_author_id"] = existing_author.id

            # Step 3: Check attempted change to any field in the unique constraint
            for field, original_value in immutable_fields.items():
                if field in data and str(data[field]) != str(original_value):
                    raise ValueError(
                        f"Cannot change '{field}' for existing Tatvapada entry (ID: {entry_id}). "
                        f"Please insert a new entry instead."
                    )

            # Step 4: Update the remaining fields
            for key, value in data.items():
                if hasattr(existing_entry, key):
                    setattr(existing_entry, key, value)

            db_instance.session.commit()
            self.logger.info(f"Updated Tatvapada entry with id: {entry_id}")
            return existing_entry

        except (ValueError, SQLAlchemyError) as e:
            db_instance.session.rollback()
            self.logger.error(f"Error updating Tatvapada: {e}")
            raise e

    def update_by_composite_keys(
            self,
            samputa_sankhye: int,
            tatvapada_sankhye: int,
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
                raise ValueError("Tatvapada entry not found with given composite keys")

            # Step 2: If author name (string) is provided, map to author ID
            author_name = data.get("tatvapadakarara_hesaru")
            if author_name:
                existing_author = TatvapadaAuthorInfo.query.filter_by(tatvapadakarara_hesaru=author_name).first()
                if not existing_author:
                    raise ValueError(f"Author '{author_name}' not found. Please add the author before updating.")
                data["tatvapada_author_id"] = existing_author.id

            # Step 3: Enforce immutability of identifying fields
            immutable_fields = {
                "samputa_sankhye": existing_entry.samputa_sankhye,
                "tatvapada_sankhye": existing_entry.tatvapada_sankhye,
                "tatvapada_author_id": existing_entry.tatvapada_author_id
            }
            for field, original_value in immutable_fields.items():
                if field in data and str(data[field]) != str(original_value):
                    raise ValueError(
                        f"Cannot change '{field}' for existing Tatvapada entry. Please insert a new entry instead.")

            # Step 4: Remove relationship field (string) before update
            if "tatvapadakarara_hesaru" in data:
                del data["tatvapadakarara_hesaru"]

            # Step 5: Update the model fields
            for key, value in data.items():
                if hasattr(existing_entry, key):
                    setattr(existing_entry, key, value)

            db_instance.session.commit()
            self.logger.info(
                f"Updated Tatvapada entry with keys: {samputa_sankhye}, {tatvapada_sankhye}, {tatvapada_author_id}")
            return existing_entry

        except (ValueError, SQLAlchemyError) as e:
            db_instance.session.rollback()
            self.logger.error(f"Error updating Tatvapada: {e}")
            raise e

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

