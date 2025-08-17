import os
from datetime import datetime, timezone, timedelta

import jwt
from dotenv import load_dotenv
from flask import (
    Blueprint, request, render_template, redirect,
    url_for, make_response, jsonify
)

from app.models.user_management import User, Admin
from app.services.user_manage_service import create_user, create_admin, bcrypt
from app.utils.logger import setup_logger

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
logger = setup_logger("auth", "auth.log")

auth_bp = Blueprint("auth", __name__)

# ------------------- Cache Control ------------------- #
@auth_bp.after_app_request
def add_cache_control(response):
    """
    Prevent browser caching of protected pages.
    """
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# ------------------- Signup ------------------- #
@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        logger.info("Signup request received")
        user_data = request.get_json()
        logger.debug(f"Signup data extracted: {user_data}")

        if not user_data or not all(user_data.values()):
            logger.warning("Signup failed: Missing fields")
            return jsonify({"error": "ಎಲ್ಲಾ ಸ್ಥಳಗಳನ್ನು ಪೂರೈಸಿ."}), 400

        create_user(**user_data)
        logger.info(f"User '{user_data['username']}' created successfully")
        return jsonify({"message": "ಬಳಕೆದಾರರನ್ನು ಯಶಸ್ವಿಯಾಗಿ ರಚಿಸಲಾಗಿದೆ."}), 201

    except ValueError as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({"error": str(e)}), 400


# ------------------- Admin Creation ------------------- #
@auth_bp.route("/admin/create", methods=["POST"])
def create_admin_route():
    try:
        logger.info("Admin creation request received")
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")

        if not username or not email:
            logger.warning("Admin creation failed: Missing username or email")
            return jsonify({"error": "Username and Email are required."}), 400

        create_admin(username=username, email=email)
        logger.info(f"Admin '{username}' created successfully")
        return jsonify({"message": "Admin created successfully."}), 201

    except ValueError as e:
        logger.error(f"Admin creation error: {str(e)}")
        return jsonify({"error": str(e)}), 400


# ------------------- Login ------------------- #
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        logger.info("Login page rendered")
        return render_template("login.html")

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    logger.info(f"Login attempt for username: {username}")

    # Try admin first
    admin = Admin.query.filter_by(username=username).first()
    if admin:
        user_type = "admin"
        user_id = admin.id
        logger.info(f"Admin '{username}' logged in successfully (password-less)")
    else:
        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            logger.warning(f"Failed login attempt for user: {username}")
            return jsonify({"error": "Invalid username or password"}), 401

        user_type = "user"
        user_id = user.id
        logger.info(f"User '{username}' logged in successfully")

    # JWT payload
    payload = {
        "user_id": user_id,
        "username": username,
        "user_type": user_type,
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp())
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    logger.debug(f"JWT issued for '{username}' with user_type '{user_type}'")

    response = make_response(jsonify({
        "message": "Login successful",
        "token": token,
        "username": username,
        "user_type": user_type
    }))
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="Lax",
        secure=False  # Set True in production with HTTPS
    )
    return response


# ------------------- Logout ------------------- #
@auth_bp.route("/logout")
def logout():
    """
    Clear the JWT cookie and redirect to login.
    """
    response = make_response(redirect(url_for("auth.login")))
    response.set_cookie("access_token", "", expires=0)
    response.set_cookie("logout_message", "logout successful", max_age=5)
    logger.info("User logged out and token cleared")
    return response
