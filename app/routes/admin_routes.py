# app/routes/admin_routes.py
from flask import request, render_template, Blueprint, jsonify
from app.services.admin_dashboard import DashboardService
from app.services.user_manage_service import (
    get_all_users_with_admin_status,
    update_user,
    update_admin_status,
    delete_user
)
from app.utils.auth_decorator import login_required

admin_bp = Blueprint("admin", __name__)

# ----------------------
# Admin dashboard page
# ----------------------
@admin_bp.route("/")
@login_required
def admin_dashboard():
    """
    Admin dashboard landing page.
    URL: /admin/
    """
    return render_template("admin_panel.html")


# ----------------------
# GET all users with admin status
# ----------------------
@admin_bp.route("/users", methods=["GET"])
@login_required
def get_users():
    """
    Returns all users with admin status as JSON.
    URL: /admin/users
    """
    return jsonify(get_all_users_with_admin_status())


# ----------------------
# PUT - Update user details (username, email, phone, admin)
# ----------------------
@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@login_required
def edit_user(user_id):
    """
    Update a user's details.
    Request JSON: { "username": str, "email": str, "phone": str, "is_admin": bool }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    updated_user = update_user(
        user_id,
        username=data.get("username"),
        email=data.get("email"),
        phone=data.get("phone"),
        is_admin=data.get("is_admin")
    )

    return jsonify({"message": "User updated", "user": {
        "id": updated_user.id,
        "username": updated_user.username,
        "email": updated_user.email,
        "phone": updated_user.phone
    }})


# ----------------------
# PUT - Update admin status only
# ----------------------
@admin_bp.route("/users/<int:user_id>/admin", methods=["PUT"])
@login_required
def toggle_admin(user_id):
    """
    Toggle or set admin status for a specific user.
    Request body: { "is_admin": true/false }
    """
    data = request.get_json()
    if "is_admin" not in data:
        return jsonify({"error": "Missing is_admin field"}), 400

    is_admin = update_admin_status(user_id, data["is_admin"])
    return jsonify({"message": "Admin status updated", "is_admin": is_admin})


# ----------------------
# DELETE - Remove a user
# ----------------------
@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@login_required
def remove_user(user_id):
    """
    Delete a user by ID (also removes admin entry if exists).
    """
    delete_user(user_id)
    return jsonify({"message": f"User with ID {user_id} deleted"})


# ----------------------
# GET admin dashboard overview stats
# ----------------------
@admin_bp.route("/overview", methods=["GET"])
@login_required
def admin_overview():
    """
    Returns admin dashboard statistics as JSON.
    URL: /admin/overview
    """
    service = DashboardService()
    stats = service.get_overview_statistics()
    return jsonify(stats)
