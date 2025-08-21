from sqlalchemy import func

from app.models.tatvapada import Tatvapada
from app.models.tatvapada_author_info import TatvapadaAuthorInfo


class RightSection:
    def __init__(self):
        pass

    def get_tatvapada_list(self, offset=0, limit=10, search=""):
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
            "tippani": row.tippani,
        }
