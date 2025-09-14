import csv
import io
from collections import defaultdict
from typing import List, Tuple
from typing import Optional

from sqlalchemy import distinct
from sqlalchemy import func, or_
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
        """
        Insert a new Tatvapada entry with author management.

        Returns the new Tatvapada instance on success.
        Raises exceptions on errors.
        """
        try:
            payload = data.copy()

            # --- Author Handling ---
            author_name = payload.pop("tatvapadakarara_hesaru", None)
            if not author_name:
                raise ValueError("tatvapadakarara_hesaru is required")

            # Find or create author
            author = TatvapadaAuthorInfo.query.filter_by(
                tatvapadakarara_hesaru=author_name
            ).first()

            if not author:
                author = TatvapadaAuthorInfo(tatvapadakarara_hesaru=author_name)
                db_instance.session.add(author)
                db_instance.session.flush()  # generate author.id

            payload["tatvapada_author_id"] = author.id

            # --- Create new Tatvapada ---
            new_entry = Tatvapada(**payload)
            db_instance.session.add(new_entry)
            db_instance.session.commit()

            self.logger.info(
                f"Inserted Tatvapada for author '{author.tatvapadakarara_hesaru}' (id={author.id})"
            )
            return new_entry

        except IntegrityError as ie:
            db_instance.session.rollback()
            self.logger.warning(f"Duplicate Tatvapada insert attempt: {ie}")
            raise IntegrityError("Duplicate Tatvapada entry", ie.params, ie.orig)

        except SQLAlchemyError as se:
            db_instance.session.rollback()
            self.logger.error(f"Database error while inserting Tatvapada: {se}", exc_info=True)
            raise

        except Exception as e:
            db_instance.session.rollback()
            self.logger.error(f"Unexpected error inserting Tatvapada: {e}", exc_info=True)
            raise

    def update_by_composite_keys(
        self,
        samputa_sankhye: float,
        tatvapada_sankhye: str,
        tatvapada_author_id: int,
        data: dict
    ) -> Optional[Tatvapada]:
        """
        Update a Tatvapada entry identified by composite keys.

        Updates allowed fields except immutable keys.
        Raises ValueError on validation and unique constraint errors.
        """
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
                update_data.pop(field, None)

            # Step 4: If author name is provided, update the author record
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

            if "tatvapada_author_info.tatvapadakarara_hesaru" in error_str:
                self.logger.warning(f"Duplicate author name attempted: {error_str}")
                raise ValueError("The author name already exists. Please choose a different name.")

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

    def delete_by_composite_keys(
        self,
        samputa_sankhye: float,
        tatvapada_sankhye: str,
        tatvapada_author_id: int
    ) -> bool:
        """
        Delete a specific Tatvapada entry given composite keys.

        Returns True if deleted, False if not found.
        """
        try:
            entry = Tatvapada.query.filter_by(
                samputa_sankhye=samputa_sankhye,
                tatvapada_sankhye=tatvapada_sankhye,
                tatvapada_author_id=tatvapada_author_id
            ).first()

            if not entry:
                raise ValueError("Tatvapada entry not found with the given composite keys.")

            db_instance.session.delete(entry)
            db_instance.session.commit()

            self.logger.info(
                f"Deleted Tatvapada entry with keys: {samputa_sankhye}, {tatvapada_sankhye}, {tatvapada_author_id}"
            )
            return True

        except ValueError as ve:
            db_instance.session.rollback()
            self.logger.warning(f"Delete validation error: {ve}")
            raise ve

        except SQLAlchemyError as sqle:
            db_instance.session.rollback()
            self.logger.error(f"Database error while deleting Tatvapada: {sqle}")
            raise ValueError("A database error occurred while deleting the Tatvapada.")

        except Exception as ex:
            db_instance.session.rollback()
            self.logger.error(f"Unexpected error during delete: {ex}")
            raise ValueError("An unexpected error occurred while deleting the Tatvapada.")

    def search_by_keyword(
            self,
            keyword: str,
            samputa: str,
            author_id: int,
            offset: int = 0,
            limit: int = 10,
    ) -> Tuple[List[Tatvapada], int]:
        """
        Search Tatvapada entries by keyword (whole-word match), samputa, and author_id.
        Supports Kannada Unicode words with ZWNJ handling.
        """
        try:
            keyword = (keyword or "").strip()
            samputa = (samputa or "").strip() or None
            author_id = int(author_id) if author_id else None

            if not keyword:
                return [], 0

            # Escape regex special chars in keyword
            escaped_keyword = keyword.replace(r"([.*+?^${}()|\[\]\\])", r"\\\1")

            # Whole-word regex with optional ZWNJ (zero-width non-joiner) around Kannada words
            # Matches: start-of-string, whitespace, punctuation, or ZWNJ boundaries
            word_bound_regex = (
                fr"(^|[[:space:][:punct:]]|‌)"  # start or space/punct or ZWNJ (U+200C)
                fr"{escaped_keyword}"
                fr"([[:space:][:punct:]]|$|‌)"  # end or space/punct or ZWNJ
            )

            # Base query with join to author
            base_q = db_instance.session.query(Tatvapada).join(
                TatvapadaAuthorInfo, Tatvapada.tatvapada_author_id == TatvapadaAuthorInfo.id
            )

            # Apply regex filter on tatvapada text or author name
            base_q = base_q.filter(
                or_(
                    Tatvapada.tatvapada.op("REGEXP")(word_bound_regex),
                    TatvapadaAuthorInfo.tatvapadakarara_hesaru.op("REGEXP")(word_bound_regex),
                )
            )

            # Optional filters
            if samputa:
                base_q = base_q.filter(func.trim(Tatvapada.samputa_sankhye) == samputa)
            if author_id:
                base_q = base_q.filter(Tatvapada.tatvapada_author_id == author_id)

            # Total count
            total = db_instance.session.query(func.count()).select_from(base_q.subquery()).scalar()

            # Pagination
            results = (
                base_q.order_by(Tatvapada.samputa_sankhye, Tatvapada.tatvapada_sankhye)
                .offset(offset)
                .limit(limit)
                .all()
            )

            return results, total

        except SQLAlchemyError as e:
            self.logger.error(f"DB error in search_by_keyword: {e}")
            return [], 0
        except ValueError as e:
            self.logger.error(f"Invalid input in search_by_keyword: {e}")
            return [], 0

    def get_all_samputa_sankhye(self) -> List[int]:
        """
        Returns a list of all distinct samputa_sankhye values (non-null).
        """
        try:
            results = Tatvapada.query.with_entities(
                distinct(Tatvapada.samputa_sankhye)
            ).all()
            return [row[0] for row in results if row is not None]
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching all samputa_sankhye: {e}")
            return []

    def get_tatvapada_sankhye_by_samputa(self, samputa_sankhye: int) -> List[int]:
        """
        Returns a list of tatvapada_sankhye integers for a given samputa_sankhye.
        """
        try:
            results = Tatvapada.query.filter_by(
                samputa_sankhye=samputa_sankhye
            ).with_entities(Tatvapada.tatvapada_sankhye).distinct().all()

            return [int(row[0]) for row in results if row is not None]
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching tatvapada_sankhye by samputa {samputa_sankhye}: {e}")
            return []

    def get_sankhyes_with_author_by_samputa(self, samputa_sankhye: int) -> List[dict]:
        """
        Returns list of dicts containing tatvapada_sankhye, author id, and author name for a samputa.
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

    def get_specific_tatvapada(
        self,
        samputa_sankhye: int,
        tatvapada_author_id: int,
        tatvapada_sankhye: str
    ) -> Optional[Tatvapada]:
        """
        Fetch a specific Tatvapada entry by composite keys.

        Returns Tatvapada object if found, else None.
        """
        try:
            return Tatvapada.query.filter_by(
                samputa_sankhye=samputa_sankhye,
                tatvapada_author_id=tatvapada_author_id,
                tatvapada_sankhye=tatvapada_sankhye
            ).first()
        except SQLAlchemyError as e:
            self.logger.error(
                f"Error fetching specific tatvapada (samputa: {samputa_sankhye}, author_id: {tatvapada_author_id}, sankhye: {tatvapada_sankhye}): {e}"
            )
            return None

    @staticmethod
    def get_all_delete_keys() -> dict:
        """
        Optimized response: groups tatvapada_sankhyes by samputa and author for delete keys.
        Returns dict with key "delete_keys".
        """
        results = (
            db_instance.session.query(
                Tatvapada.samputa_sankhye,
                Tatvapada.tatvapada_author_id,
                TatvapadaAuthorInfo.tatvapadakarara_hesaru,
                Tatvapada.tatvapada_sankhye
            )
            .join(TatvapadaAuthorInfo, Tatvapada.tatvapada_author_id == TatvapadaAuthorInfo.id)
            .order_by(Tatvapada.samputa_sankhye, Tatvapada.tatvapada_author_id, Tatvapada.tatvapada_sankhye)
            .all()
        )

        grouped = defaultdict(lambda: {"tatvapada_sankhyes": []})

        for row in results:
            key = (row.samputa_sankhye, row.tatvapada_author_id)
            grouped[key]["samputa_sankhye"] = row.samputa_sankhye
            grouped[key]["tatvapada_author_id"] = row.tatvapada_author_id
            grouped[key]["tatvapadakarara_hesaru"] = row.tatvapadakarara_hesaru
            grouped[key]["tatvapada_sankhyes"].append(row.tatvapada_sankhye)

        delete_keys = list(grouped.values())

        return {"delete_keys": delete_keys}


BULK_UPLOAD_COLUMNS = [
    'samputa_sankhye',
    'tatvapadakosha_sheershike',
    'tatvapadakarara_hesaru',
    'vibhag',
    'tatvapada_sheershike',
    'tatvapada_sankhye',
    'tatvapada_first_line',
    'tatvapada',
    'bhavanuvada',
    'klishta_padagalu_artha',
    'tippani'
]


class BulkService:
    def __init__(self, db_session=None):
        self.db = db_session or db_instance.session

    def upload_csv_records(self, file_stream) -> Tuple[int, List[str]]:
        """
        Reads CSV from file_stream and inserts Tatvapada and author records in bulk.

        Returns:
            records_added (int): Number of records successfully added.
            errors (List[str]): List of user-friendly errors encountered.
        """
        records_added = 0
        errors: List[str] = []

        try:
            file_content = file_stream.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(file_content))

            if not reader.fieldnames:
                return 0, ["CSV file has no header row."]

            header = [h.strip() for h in reader.fieldnames]
            missing_cols = set(BULK_UPLOAD_COLUMNS) - set(header)
            if missing_cols:
                return 0, [f"Missing columns in CSV header: {', '.join(missing_cols)}"]

            for i, row in enumerate(reader, 1):
                try:
                    row = {k.strip(): v for k, v in row.items()}

                    author_name = row.get('tatvapadakarara_hesaru', '').strip()
                    if not author_name:
                        errors.append(f"Row {i}: Author name missing.")
                        continue

                    author = TatvapadaAuthorInfo.query.filter_by(
                        tatvapadakarara_hesaru=author_name
                    ).first()
                    if not author:
                        author = TatvapadaAuthorInfo(tatvapadakarara_hesaru=author_name)
                        self.db.add(author)
                        try:
                            self.db.flush()
                        except IntegrityError:
                            self.db.rollback()
                            errors.append(f"Row {i}: Duplicate author '{author_name}' detected.")
                            author = TatvapadaAuthorInfo.query.filter_by(
                                tatvapadakarara_hesaru=author_name
                            ).first()
                            if not author:
                                continue  # skip this row

                    tatvapada = Tatvapada(
                        samputa_sankhye=row.get('samputa_sankhye'),
                        tatvapadakosha_sheershike=row.get('tatvapadakosha_sheershike'),
                        tatvapada_author_id=author.id,
                        vibhag=row.get('vibhag'),
                        tatvapada_sheershike=row.get('tatvapada_sheershike'),
                        tatvapada_sankhye=row.get('tatvapada_sankhye'),
                        tatvapada_first_line=row.get('tatvapada_first_line'),
                        tatvapada=row.get('tatvapada'),
                        bhavanuvada=row.get('bhavanuvada'),
                        klishta_padagalu_artha=row.get('klishta_padagalu_artha'),
                        tippani=row.get('tippani')
                    )
                    self.db.add(tatvapada)
                    try:
                        self.db.flush()
                        records_added += 1
                    except IntegrityError:
                        self.db.rollback()
                        errors.append(f"Row {i}: Duplicate Tatvapada detected (samputa '{row.get('samputa_sankhye')}', sankhye '{row.get('tatvapada_sankhye')}').")

                except Exception as row_err:
                    self.db.rollback()
                    errors.append(f"Row {i}: {str(row_err)}")

            return records_added, errors

        except UnicodeDecodeError:
            return 0, ["Failed to decode CSV. Ensure the file is UTF-8 encoded."]
        except csv.Error as csv_err:
            return 0, [f"CSV parsing error: {str(csv_err)}"]
        except Exception as e:
            return 0, [f"Unexpected error: {str(e)}"]
