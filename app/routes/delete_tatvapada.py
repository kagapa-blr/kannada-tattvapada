from flask import Blueprint, request, jsonify
from app.services.delete_service import DeleteService
from app.config.database import db_instance
from app.utils.auth_decorator import admin_required

delete_bp = Blueprint("delete_bp", __name__)
delete_service = DeleteService(db_instance.session)   # instantiate once


def success(message, data=None):
    return jsonify({"success": True, "message": message, "data": data}), 200

def error(message, code=400):
    return jsonify({"success": False, "message": message}), code


@delete_bp.route("/delete/<samputa>/<tatvapada_sankhye>/<int:author_id>", methods=["DELETE"])
@admin_required
def delete_entry(samputa, tatvapada_sankhye, author_id):
    try:
        deleted = delete_service.delete_entry(samputa, tatvapada_sankhye, author_id)
        if deleted == 0:
            return error("No matching Tatvapada found", 404)

        db_instance.session.commit()
        return success(f"Deleted Tatvapada {tatvapada_sankhye} from Samputa {samputa} (Author ID {author_id})")

    except Exception as e:
        db_instance.session.rollback()
        return error(str(e), 500)


@delete_bp.route("/delete-by-author/<author_name>", methods=["DELETE"])
@admin_required
def delete_by_author(author_name):
    try:
        deleted, author = delete_service.delete_by_author(author_name)
        if not author:
            return error(f"Author '{author_name}' not found", 404)
        if deleted == 0:
            return error(f"No Tatvapadas found for author '{author_name}'", 404)

        db_instance.session.commit()
        return success(f"Deleted {deleted} Tatvapada(s) and author '{author_name}' if no entries left")

    except Exception as e:
        db_instance.session.rollback()
        return error(str(e), 500)


@delete_bp.route("/delete-by-samputa/<samputa>", methods=["DELETE"])
@admin_required
def delete_by_samputa(samputa):
    try:
        deleted = delete_service.delete_by_samputa(samputa)
        if deleted == 0:
            return error(f"No Tatvapadas found for Samputa {samputa}", 404)

        db_instance.session.commit()
        return success(f"Deleted {deleted} Tatvapada(s) from Samputa {samputa}")

    except Exception as e:
        db_instance.session.rollback()
        return error(str(e), 500)


@delete_bp.route("/delete-by-samputa-author/<samputa>/<int:author_id>", methods=["DELETE"])
@admin_required
def delete_by_samputa_and_author(samputa, author_id):
    try:
        deleted, author_name = delete_service.delete_by_samputa_and_author(samputa, author_id)

        if not author_name:
            return error(f"Author with ID {author_id} not found", 404)

        if deleted == 0:
            return error(f"No Tatvapadas found for {author_name} in Samputa {samputa}", 404)

        db_instance.session.commit()
        return success(f"Deleted {deleted} Tatvapada(s) for {author_name} in Samputa {samputa}")

    except Exception as e:
        db_instance.session.rollback()
        return error(str(e), 500)



@delete_bp.route("/bulk-delete", methods=["DELETE"])
@admin_required
def bulk_delete():
    try:
        items = request.json.get("items", [])
        deleted = delete_service.bulk_delete(items)
        if deleted == 0:
            return error("No Tatvapadas deleted", 404)

        db_instance.session.commit()
        return success(f"Bulk deleted {deleted} Tatvapada(s)")

    except Exception as e:
        db_instance.session.rollback()
        return error(str(e), 500)
