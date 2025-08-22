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

    def get_tippanis(self, offset=0, limit=10, search=""):
        """
        Fetch paginated Tippanis with samputa, author id, author name, tippani content, and tippani_id.
        Optional search by Tippani content OR Author name.
        """
        query = (
            db_instance.session.query(
                TatvapadaTippani.tippani_id,
                TatvapadaTippani.samputa_sankhye,
                TatvapadaTippani.tatvapada_author_id,
                TatvapadaTippani.tippani_content,
                TatvapadaAuthorInfo.tatvapadakarara_hesaru
            )
            .join(TatvapadaAuthorInfo, TatvapadaTippani.tatvapada_author_id == TatvapadaAuthorInfo.id)
        )

        if search:
            search_str = f"%{search.strip()}%"
            query = query.filter(
                TatvapadaTippani.tippani_content.ilike(search_str) |
                TatvapadaAuthorInfo.tatvapadakarara_hesaru.ilike(search_str)
            )

        total = query.count()
        rows = query.offset(offset).limit(limit).all()

        results = [
            {
                "tippani_id": row.tippani_id,
                "samputa_sankhye": row.samputa_sankhye,
                "tatvapada_author_id": row.tatvapada_author_id,
                "tatvapadakarara_hesaru": row.tatvapadakarara_hesaru,
                "tippani_content": row.tippani_content
            }
            for row in rows
        ]

        return {"total": total, "results": results}

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
    def get_tippani_by_samputa_author(samputa: str, author_id: int):
        """
        Fetch Tippani entry for a given Samputa and Author ID.
        Returns dict with tippani_id and tippani_content or None.
        """
        tippani = (
            db_instance.session.query(TatvapadaTippani)
            .filter_by(samputa_sankhye=samputa, tatvapada_author_id=author_id)
            .first()
        )
        if tippani:
            return {"id": tippani.tippani_id, "content": tippani.tippani_content}
        return None

    @staticmethod
    def create_tippani(samputa: str, author_id: int, content: str):
        """
        Create a new Tippani entry with given Samputa and Author.
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
            tippani_content=str(content).strip()
        )

        db_instance.session.add(new_tippani)
        db_instance.session.commit()

        return {
            "id": new_tippani.tippani_id,
            "content": new_tippani.tippani_content
        }

    @staticmethod
    def update_tippani(tippani_id: int, content: str):
        """
        Update existing Tippani by ID.
        """
        tippani = db_instance.session.query(TatvapadaTippani).get(tippani_id)
        if not tippani:
            return None
        tippani.tippani_content = content
        db_instance.session.commit()
        return {"id": tippani.tippani_id, "content": tippani.tippani_content}

    @staticmethod
    def delete_tippani(samputa: str, author_id: int):
        """
        Delete Tippani by Samputa + Author.
        """
        tippani = (
            db_instance.session.query(TatvapadaTippani)
            .filter_by(samputa_sankhye=samputa, tatvapada_author_id=author_id)
            .first()
        )
        if not tippani:
            return False
        db_instance.session.delete(tippani)
        db_instance.session.commit()
        return True
