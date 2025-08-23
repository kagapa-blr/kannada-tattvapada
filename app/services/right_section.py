from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.config.database import db_instance
from app.models.tatvapada import Tatvapada, TatvapadaTippani, Arthakosha
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

    #---------------------TIPPANI------------------------------
    def get_all_tippanis(self, offset=0, limit=10, search=""):
        """
        Fetch paginated Tippanis with samputa, author id, author name, tippani_id.
        Optional search by Tippani title OR Author name (starts with search string).
        """
        query = (
            db_instance.session.query(
                TatvapadaTippani.tippani_id,
                TatvapadaTippani.samputa_sankhye,
                TatvapadaTippani.tatvapada_author_id,
                TatvapadaAuthorInfo.tatvapadakarara_hesaru,
                TatvapadaTippani.tippani_title
            )
            .join(TatvapadaAuthorInfo, TatvapadaTippani.tatvapada_author_id == TatvapadaAuthorInfo.id)
        )

        if search:
            search_str = f"{search.strip()}%"  # match only from start
            query = query.filter(
                TatvapadaTippani.tippani_title.ilike(search_str) |
                TatvapadaAuthorInfo.tatvapadakarara_hesaru.ilike(search_str)
            )

        total = query.count()  # total matching rows

        # Apply pagination
        rows = query.order_by(TatvapadaTippani.tippani_id).offset(offset).limit(limit).all()

        results = [
            {
                "tippani_id": row.tippani_id,
                "samputa_sankhye": row.samputa_sankhye,
                "tatvapada_author_id": row.tatvapada_author_id,
                "tatvapadakarara_hesaru": row.tatvapadakarara_hesaru,
                "tippani_title": row.tippani_title
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
    def get_tippanis_by_samputa_author(samputa: str, author_id: int):
        """
        Fetch all Tippani IDs for a given samputa and author_id.
        Returns:
        [
            {"tippani_id": 1},
            {"tippani_id": 2},
            ...
        ]
        """
        if not samputa or not author_id:
            return []

        query = (
            db_instance.session.query(TatvapadaTippani.tippani_id)
            .filter(
                TatvapadaTippani.samputa_sankhye == samputa,
                TatvapadaTippani.tatvapada_author_id == author_id,
            )
            .order_by(TatvapadaTippani.tippani_id.asc())
            .all()
        )

        return [{"tippani_id": row.tippani_id} for row in query]

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

    @staticmethod
    def get_tippani(samputa: str, author_id: int, tippani_id: int):
        """
        Fetch a specific Tippani entry by Samputa, Author ID, and Tippani ID.
        Returns dict with full details or None.
        """
        tippani = (
            db_instance.session.query(TatvapadaTippani)
            .filter_by(
                samputa_sankhye=samputa,
                tatvapada_author_id=author_id,
                tippani_id=tippani_id
            )
            .first()
        )
        if tippani:
            return {
                "id": tippani.tippani_id,
                "samputa": tippani.samputa_sankhye,
                "author_id": tippani.tatvapada_author_id,
                "title": tippani.tippani_title,
                "content": tippani.tippani_content,
            }
        return None


    @staticmethod
    def create_tippani(samputa: str, author_id: int, content: str, title: str = None):
        """
        Create a new Tippani entry with given Samputa, Author, Title, and Content.
        Ensures proper types and not null values.
        """
        if not samputa or not author_id or not content:
            raise ValueError("samputa, author_id and content are required")

        try:
            author_id = int(author_id)  # Ensure it's int
        except ValueError:
            raise ValueError("author_id must be an integer")

        new_tippani = TatvapadaTippani(
            samputa_sankhye=str(samputa).strip(),
            tatvapada_author_id=author_id,
            tippani_title=str(title).strip() if title else None,
            tippani_content=str(content).strip()
        )

        db_instance.session.add(new_tippani)
        db_instance.session.commit()

        return {
            "id": new_tippani.tippani_id,
            "samputa": new_tippani.samputa_sankhye,
            "author_id": new_tippani.tatvapada_author_id,
            "title": new_tippani.tippani_title,
            "content": new_tippani.tippani_content
        }


    @staticmethod
    def update_tippani(samputa: str, author_id: int, tippani_id: int, content: str, title: str = None):
        """
        Update existing Tippani by Samputa, Author, and Tippani ID.
        """
        tippani = (
            db_instance.session.query(TatvapadaTippani)
            .filter_by(samputa_sankhye=samputa, tatvapada_author_id=author_id, tippani_id=tippani_id)
            .first()
        )
        if not tippani:
            return None

        if content:
            tippani.tippani_content = str(content).strip()
        if title is not None:
            tippani.tippani_title = str(title).strip()

        db_instance.session.commit()

        return {
            "id": tippani.tippani_id,
            "samputa": tippani.samputa_sankhye,
            "author_id": tippani.tatvapada_author_id,
            "title": tippani.tippani_title,
            "content": tippani.tippani_content
        }


    @staticmethod
    def delete_tippani(samputa: str, author_id: int, tippani_id: int):
        """
        Delete Tippani by Samputa, Author, and Tippani ID.
        """
        tippani = (
            db_instance.session.query(TatvapadaTippani)
            .filter_by(samputa_sankhye=samputa, tatvapada_author_id=author_id, tippani_id=tippani_id)
            .first()
        )
        if not tippani:
            return False
        db_instance.session.delete(tippani)
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
