import csv
import io
from typing import Tuple, List

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.config.database import db_instance
from app.models.tatvapada import Tatvapada, Arthakosha, ParibhashikaPadavivarana
from app.models.tatvapada_author_info import TatvapadaAuthorInfo


class RightSection:
    def __init__(self):
        pass
    #--------------Tatvapada suchi -------------------
    def get_tatvapada_suchi(self, offset=0, limit=10, search=""):
        """
        Fetch paginated list of Tatvapada entries.
        Supports optional search by first line.
        """
        try:
            query = (
                Tatvapada.query
                .join(TatvapadaAuthorInfo, Tatvapada.tatvapada_author_id == TatvapadaAuthorInfo.id)
                .with_entities(
                    Tatvapada.samputa_sankhye,
                    Tatvapada.tatvapada_sankhye,
                    Tatvapada.tatvapada_author_id,
                    Tatvapada.tatvapada_first_line,
                    TatvapadaAuthorInfo.tatvapadakarara_hesaru,
                )
            )

            if search:
                query = query.filter(Tatvapada.tatvapada_first_line.ilike(f"{search.strip()}%"))

            total = query.count()
            rows = query.offset(offset).limit(limit).all()

            results = [
                {
                    "samputa_sankhye": getattr(row, "samputa_sankhye", None),
                    "tatvapada_sankhye": getattr(row, "tatvapada_sankhye", None),
                    "tatvapada_author_id": getattr(row, "tatvapada_author_id", None),
                    "tatvapadakarara_hesaru": getattr(row, "tatvapadakarara_hesaru", None),
                    "tatvapada_first_line": getattr(row, "tatvapada_first_line", None),
                }
                for row in rows
            ]

            return {"total": total, "results": results}

        except Exception as e:
            # Log error or raise for route to handle
            raise e

    def get_tatvapada_details(self, samputa_sankhye, tatvapada_author_id, tatvapada_sankhye):
        """
        Fetch a specific Tatvapada entry by (samputa, author_id, tatvapada_sankhye).
        Returns dict if found, else None. Handles missing relationships safely.
        """
        try:
            row = (
                Tatvapada.query
                .filter(
                    func.trim(Tatvapada.samputa_sankhye) == str(samputa_sankhye).strip(),
                    Tatvapada.tatvapada_author_id == int(tatvapada_author_id),
                    func.trim(Tatvapada.tatvapada_sankhye) == str(tatvapada_sankhye).strip(),
                )
                .first()
            )

            if not row:
                return None

            # Safe access for author name
            author_name = getattr(row.tatvapadakarara_hesaru, "tatvapadakarara_hesaru", None) \
                if getattr(row, "tatvapadakarara_hesaru", None) else None

            # Safe access for tippanis
            tippanis = [
                {
                    "tippani_id": getattr(t, "tippani_id", None),
                    "content": getattr(t, "tippani_content", None),
                }
                for t in getattr(row, "tippanigalu", []) or []
            ]

            return {
                "id": getattr(row, "id", None),
                "samputa_sankhye": getattr(row, "samputa_sankhye", None),
                "tatvapada_sankhye": getattr(row, "tatvapada_sankhye", None),
                "tatvapada_first_line": getattr(row, "tatvapada_first_line", None),
                "tatvapada": getattr(row, "tatvapada", None),
                "tatvapada_author_id": getattr(row, "tatvapada_author_id", None),
                "tatvapadakarara_hesaru": author_name,
                "bhavanuvada": getattr(row, "bhavanuvada", None),
                "klishta_padagalu_artha": getattr(row, "klishta_padagalu_artha", None),
                "tippanis": tippanis,
            }

        except Exception as e:
            # Propagate exception for route handling
            raise e


    @staticmethod
    def get_samputa_with_authors():
        """
        Returns a list of Samputa numbers along with authors who have entries in that Samputa.
        Output format:
        [
            {
                "samputa": "1",
                "authors": [{"id": 1, "name": "Basavaraj"}, {"id": 2, "name": "Shivakumar"}]
            },
            ...
        ]
        """
        tatvapadas = (
            db_instance.session.query(Tatvapada)
            .options(joinedload(Tatvapada.tatvapadakarara_hesaru))
            .all()
        )

        result = {}
        for t in tatvapadas:
            samputa = t.samputa_sankhye
            author = t.tatvapadakarara_hesaru
            if samputa not in result:
                result[samputa] = {}
            result[samputa][author.id] = author.tatvapadakarara_hesaru

        # Convert to list of dicts
        samputa_list = []
        for samputa, authors in result.items():
            samputa_list.append({
                "samputa": samputa,
                "authors": [{"id": aid, "name": name} for aid, name in authors.items()]
            })

        return samputa_list


    # --------------------- PARIBHASHIKA PADAVIVARANA ------------------------------
    def get_all_paribhashika_padavivarana(self, offset=0, limit=10, search=""):
        """
        Fetch paginated ParibhashikaPadavivarana entries with samputa, author id, author name, entry_id.
        Optional search by Title OR Author name (starts with search string).
        """
        query = (
            db_instance.session.query(
                ParibhashikaPadavivarana.paribhashika_padavivarana_id,
                ParibhashikaPadavivarana.samputa_sankhye,
                ParibhashikaPadavivarana.tatvapada_author_id,
                TatvapadaAuthorInfo.tatvapadakarara_hesaru,
                ParibhashikaPadavivarana.paribhashika_padavivarana_title
            )
            .join(TatvapadaAuthorInfo, ParibhashikaPadavivarana.tatvapada_author_id == TatvapadaAuthorInfo.id)
        )

        if search:
            search_str = f"{search.strip()}%"  # match only from start
            query = query.filter(
                ParibhashikaPadavivarana.paribhashika_padavivarana_title.ilike(search_str) |
                TatvapadaAuthorInfo.tatvapadakarara_hesaru.ilike(search_str)
            )

        total = query.count()  # total matching rows

        # Apply pagination
        rows = query.order_by(ParibhashikaPadavivarana.paribhashika_padavivarana_id).offset(offset).limit(limit).all()

        results = [
            {
                "id": row.paribhashika_padavivarana_id,
                "samputa_sankhye": row.samputa_sankhye,
                "tatvapada_author_id": row.tatvapada_author_id,
                "tatvapadakarara_hesaru": row.tatvapadakarara_hesaru,
                "title": row.paribhashika_padavivarana_title
            }
            for row in rows
        ]

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "results": results
        }

    @staticmethod
    def get_padavivaranas_by_samputa_author(samputa: str, author_id: int):
        """
        Fetch all Padavivarana IDs for a given samputa and author_id.

        Returns:
        [
            {"paribhashika_padavivarana_id": 1},
            {"paribhashika_padavivarana_id": 2},
            ...
        ]
        """
        if not samputa or not author_id:
            return []

        query = (
            db_instance.session.query(ParibhashikaPadavivarana.paribhashika_padavivarana_id)
            .filter(
                ParibhashikaPadavivarana.samputa_sankhye == samputa,
                ParibhashikaPadavivarana.tatvapada_author_id == author_id,
            )
            .order_by(ParibhashikaPadavivarana.paribhashika_padavivarana_id.asc())
            .all()
        )

        return [{"paribhashika_padavivarana_id": row.paribhashika_padavivarana_id} for row in query]

    @staticmethod
    def get_id_tittle_paribhashika(samputa: str, author_id: int):
        """
        Fetch all IDs and titles for a given samputa and author_id.
        Returns:
        [
            {"padavivarana_id": 1, "title": "Title 1"},
            {"padavivarana_id": 2, "title": "Title 2"},
            ...
        ]
        """
        if not samputa or not author_id:
            return []

        query = (
            db_instance.session.query(
                ParibhashikaPadavivarana.paribhashika_padavivarana_id,
                ParibhashikaPadavivarana.paribhashika_padavivarana_title
            )
            .filter(
                ParibhashikaPadavivarana.samputa_sankhye == samputa,
                ParibhashikaPadavivarana.tatvapada_author_id == author_id,
            )
            .order_by(ParibhashikaPadavivarana.paribhashika_padavivarana_id.asc())
            .all()
        )

        return [
            {
                "padavivarana_id": row.paribhashika_padavivarana_id,
                "title": row.paribhashika_padavivarana_title
            } for row in query
        ]

    @staticmethod
    def get_paribhashika_padavivarana(samputa: str, author_id: int, entry_id: int):
        """
        Fetch a specific ParibhashikaPadavivarana entry.
        """
        entry = (
            db_instance.session.query(ParibhashikaPadavivarana)
            .filter_by(
                samputa_sankhye=samputa,
                tatvapada_author_id=author_id,
                paribhashika_padavivarana_id=entry_id
            )
            .first()
        )
        if entry:
            return {
                "id": entry.paribhashika_padavivarana_id,
                "samputa": entry.samputa_sankhye,
                "author_id": entry.tatvapada_author_id,
                "title": entry.paribhashika_padavivarana_title,
                "content": entry.paribhashika_padavivarana_content,
            }
        return None

    # --- Service method ---
    @staticmethod
    def create_paribhashika_padavivarana(samputa: str, author_id: int, content: str, title: str):
        """
        Create a new ParibhashikaPadavivarana entry.
        """
        if not all([samputa, author_id, content, title]):
            raise ValueError("All fields are required.")

        # Optional: check for duplicate title per author
        exists = db_instance.session.query(ParibhashikaPadavivarana).filter_by(
            samputa_sankhye=samputa,
            tatvapada_author_id=author_id,
            paribhashika_padavivarana_title=title
        ).first()
        if exists:
            raise ValueError("Padavivarana title already exists for this author and samputa.")

        entry = ParibhashikaPadavivarana(
            samputa_sankhye=samputa,
            tatvapada_author_id=author_id,
            paribhashika_padavivarana_title=title.strip(),
            paribhashika_padavivarana_content=content.strip()
        )
        db_instance.session.add(entry)
        db_instance.session.commit()

        return {
            "id": entry.paribhashika_padavivarana_id,
            "samputa": entry.samputa_sankhye,
            "author_id": entry.tatvapada_author_id,
            "title": entry.paribhashika_padavivarana_title,
            "content": entry.paribhashika_padavivarana_content
        }

    @staticmethod
    def update_paribhashika_padavivarana(samputa: str, author_id: int, entry_id: int, content: str, title: str = None):
        """
        Update an existing ParibhashikaPadavivarana entry.
        """
        entry = (
            db_instance.session.query(ParibhashikaPadavivarana)
            .filter_by(
                samputa_sankhye=samputa,
                tatvapada_author_id=author_id,
                paribhashika_padavivarana_id=entry_id
            )
            .first()
        )
        if not entry:
            return None

        if content:
            entry.paribhashika_padavivarana_content = str(content).strip()
        if title is not None:
            entry.paribhashika_padavivarana_title = str(title).strip()

        db_instance.session.commit()

        return {
            "id": entry.paribhashika_padavivarana_id,
            "samputa": entry.samputa_sankhye,
            "author_id": entry.tatvapada_author_id,
            "title": entry.paribhashika_padavivarana_title,
            "content": entry.paribhashika_padavivarana_content
        }

    @staticmethod
    def delete_paribhashika_padavivarana(samputa: str, author_id: int, entry_id: int):
        """
        Delete a ParibhashikaPadavivarana entry.
        """
        entry = (
            db_instance.session.query(ParibhashikaPadavivarana)
            .filter_by(
                samputa_sankhye=samputa,
                tatvapada_author_id=author_id,
                paribhashika_padavivarana_id=entry_id
            )
            .first()
        )
        if not entry:
            return False
        db_instance.session.delete(entry)
        db_instance.session.commit()
        return True














# --------------------- ARTHAKOSHA -------------------------

    # ---------------- CREATE ----------------
    @staticmethod
    def create_arthakosha(samputa: str, author_id: int, title: str, word: str, meaning: str, notes: str = None):
        if not samputa or not author_id or not word or not meaning:
            raise ValueError("samputa, author_id, word, and meaning are required")

        entry = Arthakosha(
            samputa=str(samputa).strip(),
            author_id=int(author_id),
            title=str(title).strip() if title else None,
            word=str(word).strip(),
            meaning=str(meaning).strip(),
            notes=str(notes).strip() if notes else None
        )
        db_instance.session.add(entry)
        db_instance.session.commit()

        return {
            "id": entry.id,
            "samputa": entry.samputa,
            "author_id": entry.author_id,
            "title": entry.title,
            "word": entry.word,
            "meaning": entry.meaning,
            "notes": entry.notes
        }


    # ---------------- LIST ARTHAKOSHAS ----------------
    @staticmethod
    def list_arthakoshas(samputa: str = None, author_id: int = None, offset=0, limit=10, search: str = None):
        query = Arthakosha.query.join(Arthakosha.author)  # join to get author info
        if samputa:
            query = query.filter(Arthakosha.samputa == samputa)
        if author_id:
            query = query.filter(Arthakosha.author_id == author_id)
        if search:
            search_term = search.strip()
            query = query.filter(
                Arthakosha.word.ilike(f"{search_term}%") |
                Arthakosha.meaning.ilike(f"{search_term}%") |
                TatvapadaAuthorInfo.tatvapadakarara_hesaru.ilike(f"{search_term}%")
            )

        total = query.count()
        rows = query.offset(offset).limit(limit).all()

        results = [
            {
                "id": r.id,
                "samputa": r.samputa,
                "author_id": r.author_id,
                "author_name": r.author.tatvapadakarara_hesaru if r.author else None,
                "title": r.title,
                "word": r.word,
                "meaning": r.meaning,
                "notes": r.notes
            }
            for r in rows
        ]
        return {"total": total, "offset": offset, "limit": limit, "results": results}

    # ---------------- GET SINGLE ARTHAKOSHA ----------------
    @staticmethod
    def get_arthakosha(samputa: str, author_id: int, arthakosha_id: int):
        entry = Arthakosha.query.filter_by(samputa=samputa, author_id=author_id, id=arthakosha_id).first()
        if not entry:
            return None
        return {
            "id": entry.id,
            "samputa": entry.samputa,
            "author_id": entry.author_id,
            "author_name": entry.author.tatvapadakarara_hesaru if entry.author else None,
            "title": entry.title,
            "word": entry.word,
            "meaning": entry.meaning,
            "notes": entry.notes
        }

    # ---------------- UPDATE ----------------
    @staticmethod
    def update_arthakosha(samputa: str, author_id: int, arthakosha_id: int, title: str = None, word: str = None,
                          meaning: str = None, notes: str = None):
        entry = Arthakosha.query.filter_by(samputa=samputa, author_id=author_id, id=arthakosha_id).first()
        if not entry:
            return None
        if title is not None:
            entry.title = str(title).strip()
        if word is not None:
            entry.word = str(word).strip()
        if meaning is not None:
            entry.meaning = str(meaning).strip()
        if notes is not None:
            entry.notes = str(notes).strip()
        db_instance.session.commit()
        return {
            "id": entry.id,
            "samputa": entry.samputa,
            "author_id": entry.author_id,
            "title": entry.title,
            "word": entry.word,
            "meaning": entry.meaning,
            "notes": entry.notes
        }

    # ---------------- DELETE ----------------
    @staticmethod
    def delete_arthakosha(samputa: str, author_id: int, arthakosha_id: int):
        entry = Arthakosha.query.filter_by(samputa=samputa, author_id=author_id, id=arthakosha_id).first()
        if not entry:
            return False
        db_instance.session.delete(entry)
        db_instance.session.commit()
        return True






class RightSectionBulkService:
    def __init__(self, db_session=None):
        self.db = db_session or db_instance.session


    def upload_paribhashika_padavivarana_records(self, file_stream) -> Tuple[int, List[str]]:
        """
        Reads CSV from file_stream and inserts ParibhashikaPadavivarana records in bulk.

        ✅ Required columns:
            tatvapada_author_id, samputa_sankhye,
            paribhashika_padavivarana_title, paribhashika_padavivarana_content
        """
        records_added = 0
        errors: List[str] = []

        try:
            file_content = file_stream.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(file_content))

            if not reader.fieldnames:
                return 0, ["CSV file has no header row."]

            required_cols = {
                "tatvapada_author_id",
                "samputa_sankhye",
                "paribhashika_padavivarana_title",
                "paribhashika_padavivarana_content"
            }

            # Check required columns
            print(reader.fieldnames)
            missing_cols = required_cols - set(reader.fieldnames)
            if missing_cols:
                return 0, [f"Missing columns: {', '.join(missing_cols)}"]

            for i, row in enumerate(reader, 1):
                try:
                    padavivarana = ParibhashikaPadavivarana(
                        tatvapada_author_id=row.get("tatvapada_author_id"),
                        samputa_sankhye=row.get("samputa_sankhye"),
                        paribhashika_padavivarana_title=row.get("paribhashika_padavivarana_title"),
                        paribhashika_padavivarana_content=row.get("paribhashika_padavivarana_content"),
                    )
                    self.db.add(padavivarana)
                    self.db.flush()
                    records_added += 1

                except IntegrityError:
                    self.db.rollback()
                    errors.append(
                        f"Row {i}: Duplicate entry (author + title must be unique) or invalid tatvapada_author_id")
                except Exception as row_err:
                    self.db.rollback()
                    errors.append(f"Row {i}: {str(row_err)}")

            return records_added, errors

        except Exception as e:
            return 0, [f"Unexpected error: {str(e)}"]

    def upload_arthakosha_records(self, file_stream) -> Tuple[int, List[str]]:
        """
        Reads CSV from file_stream and inserts Arthakosha records in bulk.
        Expected columns: samputa, author_id, title, word, meaning, notes
        """
        records_added = 0
        errors: List[str] = []
        try:
            file_content = file_stream.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(file_content))

            if not reader.fieldnames:
                return 0, ["CSV file has no header row."]

            required_cols = {"samputa", "author_id", "title", "word", "meaning", "notes"}
            missing_cols = required_cols - set(reader.fieldnames)
            if missing_cols:
                return 0, [f"Missing columns: {', '.join(missing_cols)}"]

            for i, row in enumerate(reader, 1):
                try:
                    arthakosha = Arthakosha(
                        samputa=row.get("samputa"),
                        author_id=row.get("author_id"),
                        title=row.get("title"),
                        word=row.get("word"),
                        meaning=row.get("meaning"),
                        notes=row.get("notes"),
                    )
                    self.db.add(arthakosha)
                    self.db.flush()
                    records_added += 1
                except IntegrityError:
                    self.db.rollback()
                    errors.append(f"Row {i}: Duplicate entry for word '{row.get('word')}'")
                except Exception as row_err:
                    self.db.rollback()
                    errors.append(f"Row {i}: {str(row_err)}")

            return records_added, errors
        except Exception as e:
            return 0, [f"Unexpected error: {str(e)}"]


