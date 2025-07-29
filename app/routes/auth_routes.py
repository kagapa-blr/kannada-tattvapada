import os
from datetime import datetime, timezone, timedelta

import jwt
from dotenv import load_dotenv
from flask import (
    Blueprint, request, render_template, redirect,
    url_for, flash, make_response
)
from app.models.user_management import User, Admin
from app.services.user_manage_service import create_user, create_admin, bcrypt

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        user_data = {
            "name": request.form.get("name"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email"),
            "username": request.form.get("username"),
            "password": request.form.get("password"),
        }

        if not all(user_data.values()):
            error = "ಎಲ್ಲಾ ಸ್ಥಳಗಳನ್ನು ಪೂರೈಸಿ."
            return render_template("login.html", error=error)

        create_user(**user_data)
        flash("ಬಳಕೆದಾರರನ್ನು ಯಶಸ್ವಿಯಾಗಿ ರಚಿಸಲಾಗಿದೆ.", "success")
        return redirect(url_for("auth.login"))

    except ValueError as e:
        return render_template("login.html", error=str(e))

@auth_bp.route("/admin/create", methods=["POST"])
def create_admin_route():
    try:
        username = request.form.get("username")
        email = request.form.get("email")

        if not username or not email:
            return "Username and Email are required.", 400

        create_admin(username=username, email=email)
        return "Admin created successfully.", 201
    except ValueError as e:
        return str(e), 400


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    user_type = None
    user_id = None

    # Try admin first
    admin = Admin.query.filter_by(username=username).first()
    if admin:
        user_type = "admin"
        user_id = admin.id
        # Admin login is password-less (adjust if needed)
    else:
        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            error = "ತಪ್ಪು ಬಳಕೆದಾರಹೆಸರು ಅಥವಾ ಗುಪ್ತಪದ"
            return render_template("login.html", error=error)

        user_type = "user"
        user_id = user.id

    # JWT payload with expiry and user_type
    payload = {
        "user_id": user_id,
        "username": username,
        "user_type": user_type,
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp())
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # Set cookie
    response = make_response(redirect(url_for("home.home_page")))
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="Lax",
        secure=False  # ✅ Set to True if using HTTPS
    )
    return response

@auth_bp.route("/logout")
def logout():
    response = make_response(redirect(url_for("auth.login")))
    response.set_cookie("access_token", "", expires=0)
    flash("ಲಾಗ್ ಔಟ್ ಯಶಸ್ವಿಯಾಗಿ.", "info")
    return response
