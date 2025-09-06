# app/routes/admin_routes.py
from flask import request, render_template, Blueprint, jsonify, g
from werkzeug.exceptions import BadRequest

from app.config.database import db_instance
from app.services.admin_dashboard import DashboardService
from app.services.user_manage_service import UserService

from app.utils.auth_decorator import login_required, admin_required
from app.utils.logger import setup_logger

admin_bp = Blueprint("admin", __name__)
logger = setup_logger(name="admin_bp")

user_service = UserService()
# ----------------------
# Admin dashboard page
# ----------------------
@admin_bp.route("/")
@login_required
def admin_dashboard():
    logger.info(f"User '{getattr(g, 'user', None)}' accessed admin dashboard")
    return render_template("admin_panel.html")


# ----------------------
# GET all users with admin status
# ----------------------
@admin_bp.route("/users", methods=["GET"])
@login_required
def get_users():
    logger.info(f"User '{g.user.username}' requested all users list")
    users = user_service.get_all_users_with_admin_status()
    logger.debug(f"Users fetched: {users}")
    return jsonify(users)


# ----------------------
# PUT - Update user details (username, email, phone, admin)
# ----------------------
@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def edit_user(user_id):
    data = request.get_json()
    if not data:
        logger.error(f"Admin '{g.user.username}' tried updating user {user_id} with no data")
        return jsonify({"error": "No data provided"}), 400

    logger.info(f"Admin '{g.user.username}' updating user {user_id} with data: {data}")
    updated_user = user_service.update_user(
        user_id,
        username=data.get("username"),
        email=data.get("email"),
        phone=data.get("phone"),
        is_admin=data.get("is_admin")
    )
    logger.info(f"User {user_id} updated successfully by '{g.user.username}'")

    return jsonify({
        "message": "User updated",
        "user": {
            "id": updated_user.id,
            "username": updated_user.username,
            "email": updated_user.email,
            "phone": updated_user.phone
        }
    })


# ----------------------
# PUT - Update admin status only
# ----------------------
@admin_bp.route("/users/<int:user_id>/admin", methods=["PUT"])
@admin_required
def toggle_admin(user_id):
    data = request.get_json()
    if "is_admin" not in data:
        logger.error(f"Admin '{g.user.username}' tried toggling admin for user {user_id} without 'is_admin' field")
        return jsonify({"error": "Missing is_admin field"}), 400

    logger.info(f"Admin '{g.user.username}' updating admin status for user {user_id} → {data['is_admin']}")
    is_admin = user_service.update_admin_status(user_id, data["is_admin"])
    logger.info(f"Admin status for user {user_id} set to {is_admin} by '{g.user.username}'")
    return jsonify({"message": "Admin status updated", "is_admin": is_admin})


# ----------------------
# DELETE - Remove a user
# ----------------------
@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def remove_user(user_id):
    logger.info(f"Admin '{g.user.username}' deleting user {user_id}")
    user_service.delete_user(user_id)
    logger.info(f"User {user_id} deleted successfully by '{g.user.username}'")
    return jsonify({"message": f"User with ID {user_id} deleted"})


# ----------------------
# GET admin dashboard overview stats
# ----------------------
@admin_bp.route("/overview", methods=["GET"])
@login_required
def admin_overview():
    logger.info(f"User '{g.user.username}' requested admin overview stats")
    service = DashboardService()
    stats = service.get_overview_statistics()
    #logger.debug(f"Overview stats: {stats}")
    return jsonify(stats)


# ----------------------
# POST - Reset user password
# ----------------------
@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@admin_required
def admin_reset_password(user_id):
    try:
        data = request.get_json()
        new_password = data.get("new_password")
        logger.info(f"Admin '{g.user.username}' resetting password for user {user_id}")

        user_service.reset_user_password(user_id, new_password)

        logger.info(f"Password reset successfully for user {user_id} by '{g.user.username}'")
        return jsonify({
            "success": True,
            "message": f"Password reset successfully for user {user_id}."
        })

    except Exception as e:
        db_instance.session.rollback()
        logger.error(f"Error resetting password for user {user_id}: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400
