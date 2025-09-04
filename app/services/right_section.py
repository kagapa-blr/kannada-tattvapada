import csv
import io
from typing import Tuple, List
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from app.config.database import db_instance
from app.models.documents import TatvapadakararaVivara
from app.models.tatvapada import Tatvapada, Arthakosha, ParibhashikaPadavivarana
from app.models.tatvapada_author_info import TatvapadaAuthorInfo


# ----------------- Tatvapada Service -----------------
class TatvapadaSuchiService:
    """Service to manage Tatvapada entries and related queries"""

    @staticmethod
    def get_tatvapada_suchi(offset=0, limit=10, search=""):
        """Fetch paginated list of Tatvapada entries."""
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
            raise e

    @staticmethod
    def get_tatvapada_details(samputa_sankhye, tatvapada_author_id, tatvapada_sankhye):
        """Fetch a specific Tatvapada entry by (samputa, author_id, tatvapada_sankhye)."""
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

            author_name = getattr(row.tatvapadakarara_hesaru, "tatvapadakarara_hesaru", None) \
                if getattr(row, "tatvapadakarara_hesaru", None) else None
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
            raise e

    @staticmethod
    def get_samputa_with_authors():
        """Return list of Samputa numbers with authors."""
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

        return [
            {"samputa": samputa, "authors": [{"id": aid, "name": name} for aid, name in authors.items()]}
            for samputa, authors in result.items()
        ]


# ----------------- ParibhashikaPadavivarana Service -----------------
class ParibhashikaPadavivaranaService:
    """Service to manage ParibhashikaPadavivarana entries."""

    @staticmethod
    def get_all(offset=0, limit=10, search=""):
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
            search_str = f"{search.strip()}%"
            query = query.filter(
                ParibhashikaPadavivarana.paribhashika_padavivarana_title.ilike(search_str) |
                TatvapadaAuthorInfo.tatvapadakarara_hesaru.ilike(search_str)
            )

        total = query.count()
        rows = query.order_by(ParibhashikaPadavivarana.paribhashika_padavivarana_id).offset(offset).limit(limit).all()

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "results": [
                {
                    "id": row.paribhashika_padavivarana_id,
                    "samputa_sankhye": row.samputa_sankhye,
                    "tatvapada_author_id": row.tatvapada_author_id,
                    "tatvapadakarara_hesaru": row.tatvapadakarara_hesaru,
                    "title": row.paribhashika_padavivarana_title
                }
                for row in rows
            ]
        }

    @staticmethod
    def get_by_samputa_author(samputa: str, author_id: int):
        return [
            {"paribhashika_padavivarana_id": row.paribhashika_padavivarana_id}
            for row in db_instance.session.query(ParibhashikaPadavivarana.paribhashika_padavivarana_id)
                .filter_by(samputa_sankhye=samputa, tatvapada_author_id=author_id)
                .order_by(ParibhashikaPadavivarana.paribhashika_padavivarana_id.asc())
                .all()
        ]

    @staticmethod
    def get_id_title(samputa: str, author_id: int):
        return [
            {"padavivarana_id": row.paribhashika_padavivarana_id, "title": row.paribhashika_padavivarana_title}
            for row in db_instance.session.query(
                ParibhashikaPadavivarana.paribhashika_padavivarana_id,
                ParibhashikaPadavivarana.paribhashika_padavivarana_title
            )
                .filter_by(samputa_sankhye=samputa, tatvapada_author_id=author_id)
                .order_by(ParibhashikaPadavivarana.paribhashika_padavivarana_id.asc())
                .all()
        ]

    @staticmethod
    def get_entry(samputa: str, author_id: int, entry_id: int):
        entry = db_instance.session.query(ParibhashikaPadavivarana).filter_by(
            samputa_sankhye=samputa,
            tatvapada_author_id=author_id,
            paribhashika_padavivarana_id=entry_id
        ).first()
        if entry:
            return {
                "id": entry.paribhashika_padavivarana_id,
                "samputa": entry.samputa_sankhye,
                "author_id": entry.tatvapada_author_id,
                "title": entry.paribhashika_padavivarana_title,
                "content": entry.paribhashika_padavivarana_content,
            }
        return None

    @staticmethod
    def create(samputa: str, author_id: int, content: str, title: str):
        if not all([samputa, author_id, content, title]):
            raise ValueError("All fields are required.")

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
    def update(samputa: str, author_id: int, entry_id: int, content: str, title: str = None):
        entry = db_instance.session.query(ParibhashikaPadavivarana).filter_by(
            samputa_sankhye=samputa,
            tatvapada_author_id=author_id,
            paribhashika_padavivarana_id=entry_id
        ).first()
        if not entry:
            return None

        if content:
            entry.paribhashika_padavivarana_content = content.strip()
        if title is not None:
            entry.paribhashika_padavivarana_title = title.strip()

        db_instance.session.commit()
        return {
            "id": entry.paribhashika_padavivarana_id,
            "samputa": entry.samputa_sankhye,
            "author_id": entry.tatvapada_author_id,
            "title": entry.paribhashika_padavivarana_title,
            "content": entry.paribhashika_padavivarana_content
        }

    @staticmethod
    def delete(samputa: str, author_id: int, entry_id: int):
        entry = db_instance.session.query(ParibhashikaPadavivarana).filter_by(
            samputa_sankhye=samputa,
            tatvapada_author_id=author_id,
            paribhashika_padavivarana_id=entry_id
        ).first()
        if not entry:
            return False
        db_instance.session.delete(entry)
        db_instance.session.commit()
        return True


# ----------------- Arthakosha Service -----------------
class ArthakoshaService:
    """Service to manage Arthakosha entries"""

    @staticmethod
    def create(samputa: str, author_id: int, title: str, word: str, meaning: str, notes: str = None):
        if not samputa or not author_id or not word or not meaning:
            raise ValueError("samputa, author_id, word, and meaning are required")

        if title:
            existing = Arthakosha.query.filter_by(author_id=int(author_id), title=title.strip()).first()
            if existing:
                raise ValueError(f"Arthakosha title '{title}' already exists for this author")

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

    @staticmethod
    def list(samputa: str = None, author_id: int = None, offset=0, limit=10, search: str = None):
        query = Arthakosha.query.join(Arthakosha.author)
        if samputa:
            query = query.filter(Arthakosha.samputa == samputa)
        if author_id:
            query = query.filter(Arthakosha.author_id == author_id)
        if search:
            term = search.strip()
            query = query.filter(
                Arthakosha.word.ilike(f"{term}%") |
                Arthakosha.meaning.ilike(f"{term}%") |
                TatvapadaAuthorInfo.tatvapadakarara_hesaru.ilike(f"{term}%")
            )

        total = query.count()
        rows = query.offset(offset).limit(limit).all()
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "results": [
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
        }

    @staticmethod
    def get(samputa: str, author_id: int, arthakosha_id: int):
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

    @staticmethod
    def update(samputa: str, author_id: int, arthakosha_id: int, title: str = None, word: str = None,
               meaning: str = None, notes: str = None):
        entry = Arthakosha.query.filter_by(samputa=samputa, author_id=author_id, id=arthakosha_id).first()
        if not entry:
            return None
        if title and title.strip() != entry.title:
            existing = Arthakosha.query.filter_by(author_id=author_id, title=title.strip()).first()
            if existing:
                raise ValueError(f"Arthakosha title '{title}' already exists for this author")
        if title is not None:
            entry.title = title.strip()
        if word is not None:
            entry.word = word.strip()
        if meaning is not None:
            entry.meaning = meaning.strip()
        if notes is not None:
            entry.notes = notes.strip()
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

    @staticmethod
    def delete(samputa: str, author_id: int, arthakosha_id: int):
        entry = Arthakosha.query.filter_by(samputa=samputa, author_id=author_id, id=arthakosha_id).first()
        if not entry:
            return False
        db_instance.session.delete(entry)
        db_instance.session.commit()
        return True

    @staticmethod
    def get_by_samputa_author(samputa: str, author_id: int):
        rows = Arthakosha.query.join(Arthakosha.author).filter(
            Arthakosha.samputa == samputa,
            Arthakosha.author_id == author_id
        ).all()
        return [
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


# ----------------- Bulk Upload Service -----------------
class BulkUploadService:
    """Service to handle bulk CSV uploads for ParibhashikaPadavivarana and Arthakosha"""

    def __init__(self, db_session=None):
        self.db = db_session or db_instance.session

    def upload_paribhashika_padavivarana(self, file_stream) -> Tuple[int, List[str]]:
        """Bulk upload ParibhashikaPadavivarana from CSV."""
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
                "paribhashika_padavivarana_content",
            }
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
                    records_added += 1
                except IntegrityError:
                    self.db.rollback()
                    errors.append(f"Row {i}: Duplicate entry or invalid tatvapada_author_id")
                except Exception as row_err:
                    self.db.rollback()
                    errors.append(f"Row {i}: {str(row_err)}")
            self.db.commit()  #  commit after loop
            return records_added, errors
        except Exception as e:
            self.db.rollback()
            return 0, [f"Unexpected error: {str(e)}"]

    def upload_arthakosha(self, file_stream) -> Tuple[int, List[str]]:
        """Bulk upload Arthakosha from CSV"""
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
                if not row.get("samputa") or not row.get("author_id") or not row.get("title") \
                        or not row.get("word") or not row.get("meaning"):
                    errors.append(f"Row {i}: Missing required field(s).")
                    continue
                try:
                    arthakosha = Arthakosha(
                        samputa=row.get("samputa").strip(),
                        author_id=int(row.get("author_id")),
                        title=row.get("title").strip(),
                        word=row.get("word").strip(),
                        meaning=row.get("meaning").strip(),
                        notes=row.get("notes").strip() if row.get("notes") else None,
                    )
                    self.db.add(arthakosha)
                    self.db.flush()
                    records_added += 1
                except IntegrityError:
                    self.db.rollback()
                    errors.append(f"Row {i}: Duplicate title '{row.get('title')}' for author_id {row.get('author_id')}")
                except Exception as row_err:
                    self.db.rollback()
                    errors.append(f"Row {i}: {str(row_err)}")
            return records_added, errors
        except Exception as e:
            return 0, [f"Unexpected error: {str(e)}"]


# ----------------- TatvapadakararaVivara Service -----------------
class TatvapadakararaVivaraService:

    @staticmethod
    def create_author(author_name, content):
        try:
            new_author = TatvapadakararaVivara(
                author_name=author_name,
                content=content
            )
            db_instance.session.add(new_author)
            db_instance.session.commit()
            return new_author, None
        except IntegrityError:
            db_instance.session.rollback()
            return None, "Author with this name already exists"

    @staticmethod
    def get_all_authors():
        """Return ID, name, created_at, and updated_at (not full content)."""
        return TatvapadakararaVivara.query.with_entities(
            TatvapadakararaVivara.id,
            TatvapadakararaVivara.author_name,
            TatvapadakararaVivara.created_at,
            TatvapadakararaVivara.updated_at
        ).all()

    @staticmethod
    def get_author_by_id(author_id):
        return TatvapadakararaVivara.query.get(author_id)

    @staticmethod
    def update_author(author_id, author_name=None, content=None):
        author = TatvapadakararaVivara.query.get(author_id)
        if not author:
            return None, "Author not found"

        if author_name:
            author.author_name = author_name
        if content:
            author.content = content

        db_instance.session.commit()
        return author, None

    @staticmethod
    def delete_author(author_id):
        author = TatvapadakararaVivara.query.get(author_id)
        if not author:
            return False, "Author not found"

        db_instance.session.delete(author)
        db_instance.session.commit()
        return True, None