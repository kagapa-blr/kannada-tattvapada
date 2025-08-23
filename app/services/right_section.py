from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.config.database import db_instance
from app.models.tatvapada import Tatvapada, TatvapadaTippani
from app.models.tatvapada_author_info import TatvapadaAuthorInfo


class RightSection:
    def __init__(self):
        pass

    def get_tatvapada_suchi(self, offset=0, limit=10, search=""):
        """
        Fetch paginated list of Tatvapada entries.
        Supports optional search by first line.
        """
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
                "samputa_sankhye": row.samputa_sankhye,
                "tatvapada_sankhye": row.tatvapada_sankhye,
                "tatvapada_author_id": row.tatvapada_author_id,
                "tatvapadakarara_hesaru": row.tatvapadakarara_hesaru,
                "tatvapada_first_line": row.tatvapada_first_line,
            }
            for row in rows
        ]

        return {"total": total, "results": results}
    def get_tatvapada_details(self, samputa_sankhye, tatvapada_author_id, tatvapada_sankhye):
        """
        Fetch a specific Tatvapada entry by (samputa, author_id, tatvapada_sankhye).
        Returns dict if found, else None.
        """
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

        return {
            "id": row.id,
            "samputa_sankhye": row.samputa_sankhye,
            "tatvapada_sankhye": row.tatvapada_sankhye,
            "tatvapada_first_line": row.tatvapada_first_line,
            "tatvapada": row.tatvapada,
            "tatvapada_author_id": row.tatvapada_author_id,
            "tatvapadakarara_hesaru": (
                row.tatvapadakarara_hesaru.tatvapadakarara_hesaru
                if row.tatvapadakarara_hesaru else None
            ),
            "bhavanuvada": row.bhavanuvada,
            "klishta_padagalu_artha": row.klishta_padagalu_artha,
            "tippanis": [
                {
                    "tippani_id": t.tippani_id,
                    "content": t.tippani_content,
                }
                for t in row.tippanigalu
            ],
        }

    #---------------------------------------------------
    def get_all_tippanis(self, offset=0, limit=10, search=""):
        """
        Fetch paginated Tippanis with samputa, author id, author name, tippani_id.
        Optional search by Tippani title OR Author name.
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
            search_str = f"%{search.strip()}%"
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
