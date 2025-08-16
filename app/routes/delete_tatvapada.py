from flask import Blueprint, request, jsonify
from app.config.database import db_instance
from app.models.tatvapada import Tatvapada
from app.models.tatvapada_author_info import TatvapadaAuthorInfo


delete_bp = Blueprint("delete_bp",__name__)


# ---------------------------
# Utility functions
# ---------------------------
def success(message, data=None):
    return jsonify({"success": True, "message": message, "data": data}), 200

def error(message, code=400):
    return jsonify({"success": False, "message": message}), code


def cleanup_author_if_unused(author_id):
    """Delete author if no Tatvapadas remain"""
    remaining = Tatvapada.query.filter_by(tatvapada_author_id=author_id).count()
    if remaining == 0:
        author = TatvapadaAuthorInfo.query.get(author_id)
        if author:
            db_instance.session.delete(author)
    return


# ---------------------------
# Delete by composite keys
# ---------------------------
@delete_bp.route("/delete/<samputa>/<tatvapada_sankhye>/<int:author_id>", methods=["DELETE"])
def delete_entry(samputa, tatvapada_sankhye, author_id):
    try:
        deleted = Tatvapada.query.filter_by(
            samputa_sankhye=samputa,
            tatvapada_sankhye=tatvapada_sankhye,
            tatvapada_author_id=author_id
        ).delete(synchronize_session=False)

        if deleted == 0:
            return error("No matching Tatvapada found", 404)

        cleanup_author_if_unused(author_id)
        db_instance.session.commit()
        return success(f"Deleted Tatvapada {tatvapada_sankhye} from Samputa {samputa} (Author ID {author_id})")

    except Exception as e:
        db_instance.session.rollback()
        return error(str(e), 500)


# ---------------------------
# Delete by author name
# ---------------------------
@delete_bp.route("/delete-by-author/<author_name>", methods=["DELETE"])
def delete_by_author(author_name):
    try:
        author = TatvapadaAuthorInfo.query.filter_by(
            tatvapadakarara_hesaru=author_name
        ).first()

        if not author:
            return error(f"Author '{author_name}' not found", 404)

        deleted = Tatvapada.query.filter_by(
            tatvapada_author_id=author.id
        ).delete(synchronize_session=False)

        if deleted == 0:
            return error(f"No Tatvapadas found for author '{author_name}'", 404)

        cleanup_author_if_unused(author.id)
        db_instance.session.commit()
        return success(f"Deleted {deleted} Tatvapada(s) and author '{author_name}' if no entries left")

    except Exception as e:
        db_instance.session.rollback()
        return error(str(e), 500)


# ---------------------------
# Delete by samputa
# ---------------------------
@delete_bp.route("/delete-by-samputa/<samputa>", methods=["DELETE"])
def delete_by_samputa(samputa):
    try:
        # Find all authors linked to this samputa
        authors = db_instance.session.query(Tatvapada.tatvapada_author_id).filter_by(
            samputa_sankhye=samputa
        ).distinct().all()
        author_ids = [a[0] for a in authors]

        deleted = Tatvapada.query.filter_by(
            samputa_sankhye=samputa
        ).delete(synchronize_session=False)

        if deleted == 0:
            return error(f"No Tatvapadas found for Samputa {samputa}", 404)

        # Cleanup unused authors
        for aid in author_ids:
            cleanup_author_if_unused(aid)

        db_instance.session.commit()
        return success(f"Deleted {deleted} Tatvapada(s) from Samputa {samputa}")

    except Exception as e:
        db_instance.session.rollback()
        return error(str(e), 500)


# ---------------------------
# Delete by samputa + author name
# ---------------------------
@delete_bp.route("/delete-by-samputa-author/<samputa>/<author_name>", methods=["DELETE"])
def delete_by_samputa_and_author(samputa, author_name):
    try:
        author = TatvapadaAuthorInfo.query.filter_by(
            tatvapadakarara_hesaru=author_name
        ).first()

        if not author:
            return error(f"Author '{author_name}' not found", 404)

        deleted = Tatvapada.query.filter_by(
            samputa_sankhye=samputa,
            tatvapada_author_id=author.id
        ).delete(synchronize_session=False)

        if deleted == 0:
            return error(f"No Tatvapadas found for {author_name} in Samputa {samputa}", 404)

        cleanup_author_if_unused(author.id)
        db_instance.session.commit()
        return success(f"Deleted {deleted} Tatvapada(s) for {author_name} in Samputa {samputa}")

    except Exception as e:
        db_instance.session.rollback()
        return error(str(e), 500)



# Bulk Delete (from JS "Delete Selected")
# ---------------------------
@delete_bp.route("/bulk-delete", methods=["DELETE"])
def bulk_delete():
    try:
        items = request.json.get("items", [])
        total_deleted = 0
        author_ids = set()

        for item in items:
            samputa = item.get("samputa")
            author_id = item.get("authorId")
            sankhya = item.get("sankhya")  # <- use the selected tatvapada number
            if not samputa or not author_id or not sankhya:
                continue

            deleted = Tatvapada.query.filter_by(
                samputa_sankhye=samputa,
                tatvapada_author_id=author_id,
                tatvapada_sankhye=sankhya  # <- only delete this specific Tatvapada
            ).delete(synchronize_session=False)

            total_deleted += deleted
            author_ids.add(author_id)

        # Cleanup unused authors
        for aid in author_ids:
            cleanup_author_if_unused(aid)

        if total_deleted == 0:
            return error("No Tatvapadas deleted", 404)

        db_instance.session.commit()
        return success(f"Bulk deleted {total_deleted} Tatvapada(s)")

    except Exception as e:
        db_instance.session.rollback()
        return error(str(e), 500)
