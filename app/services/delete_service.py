from app.config.database import db_instance
from app.models.tatvapada import Tatvapada
from app.models.tatvapada_author_info import TatvapadaAuthorInfo


class DeleteService:
    def __init__(self, db_session=None):
        # Allow injection of a custom session (for tests)
        self.db = db_session or db_instance.session

    # ---------------------------
    # Utility
    # ---------------------------
    def cleanup_author_if_unused(self, author_id):
        """Delete author if no Tatvapadas remain"""
        remaining = Tatvapada.query.filter_by(tatvapada_author_id=author_id).count()
        if remaining == 0:
            author = TatvapadaAuthorInfo.query.get(author_id)
            if author:
                self.db.delete(author)

    # ---------------------------
    # Delete operations
    # ---------------------------
    def delete_entry(self, samputa, tatvapada_sankhye, author_id):
        deleted = Tatvapada.query.filter_by(
            samputa_sankhye=samputa,
            tatvapada_sankhye=tatvapada_sankhye,
            tatvapada_author_id=author_id
        ).delete(synchronize_session=False)

        if deleted > 0:
            self.cleanup_author_if_unused(author_id)

        return deleted

    def delete_by_author(self, author_name):
        author = TatvapadaAuthorInfo.query.filter_by(
            tatvapadakarara_hesaru=author_name
        ).first()

        if not author:
            return 0, None

        deleted = Tatvapada.query.filter_by(
            tatvapada_author_id=author.id
        ).delete(synchronize_session=False)

        if deleted > 0:
            self.cleanup_author_if_unused(author.id)

        return deleted, author

    def delete_by_samputa(self, samputa):
        authors = self.db.query(Tatvapada.tatvapada_author_id).filter_by(
            samputa_sankhye=samputa
        ).distinct().all()
        author_ids = [a[0] for a in authors]

        deleted = Tatvapada.query.filter_by(
            samputa_sankhye=samputa
        ).delete(synchronize_session=False)

        for aid in author_ids:
            self.cleanup_author_if_unused(aid)

        return deleted

    def delete_by_samputa_and_author(self, samputa, author_name):
        author = TatvapadaAuthorInfo.query.filter_by(
            tatvapadakarara_hesaru=author_name
        ).first()
        if not author:
            return 0, None

        deleted = Tatvapada.query.filter_by(
            samputa_sankhye=samputa,
            tatvapada_author_id=author.id
        ).delete(synchronize_session=False)

        if deleted > 0:
            self.cleanup_author_if_unused(author.id)

        return deleted, author

    def bulk_delete(self, items):
        total_deleted = 0
        author_ids = set()

        for item in items:
            samputa = item.get("samputa")
            author_id = item.get("authorId")
            sankhya = item.get("sankhya")

            if not samputa or not author_id or not sankhya:
                continue

            deleted = Tatvapada.query.filter_by(
                samputa_sankhye=samputa,
                tatvapada_author_id=author_id,
                tatvapada_sankhye=sankhya
            ).delete(synchronize_session=False)

            total_deleted += deleted
            author_ids.add(author_id)

        for aid in author_ids:
            self.cleanup_author_if_unused(aid)

        return total_deleted
