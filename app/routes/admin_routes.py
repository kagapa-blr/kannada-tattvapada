# app/routes/admin_routes.py

from flask import request, redirect, url_for, flash, render_template, Blueprint
from app.config.database import db_instance
from app.models.user_management import User, Admin
from app.utils.auth_decorator import login_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/")
@login_required
def admin_dashboard():
    """
    Admin dashboard landing page.
    URL: /admin/
    """
    return render_template("admin_panel.html")


@admin_bp.route("/users", methods=["GET"])
@login_required
def user_management():
    """
    Display all users with option to promote/demote as admin.
    URL: /admin/users
    """
    users = User.query.all()
    admin_usernames = {admin.username for admin in Admin.query.all()}
    return render_template("user_management.html", users=users, admin_usernames=admin_usernames)


@admin_bp.route("/users/save", methods=["POST"])
@login_required
def save_user_changes():
    """
    Save user updates (username, phone, email) and handle admin toggling.
    URL: /admin/users/save
    """
    users = User.query.all()
    current_admins = {admin.username: admin for admin in Admin.query.all()}

    for user in users:
        new_username = request.form.get(f"username_{user.id}", user.username)
        new_phone = request.form.get(f"phone_{user.id}", user.phone)
        new_email = request.form.get(f"email_{user.id}", user.email)
        make_admin = request.form.get(f"is_admin_{user.id}") == "on"

        # Update user fields
        user.username = new_username
        user.phone = new_phone
        user.email = new_email

        # Admin toggle logic
        if make_admin and user.username not in current_admins:
            db_instance.session.add(Admin(username=user.username, email=user.email))
        elif not make_admin and user.username in current_admins:
            db_instance.session.delete(current_admins[user.username])

    db_instance.session.commit()
    flash("User changes saved successfully.", "success")
    return redirect(url_for("admin.user_management"))
