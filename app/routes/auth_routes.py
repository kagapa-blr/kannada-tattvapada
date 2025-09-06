import os
from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from dotenv import load_dotenv
from flask import (
    Blueprint, request, render_template, make_response, jsonify
)

from app.models.user_management import User, Admin
from app.services.user_manage_service import UserService
from app.utils.auth_decorator import admin_required
from app.utils.logger import setup_logger

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is missing from environment variables")

logger = setup_logger("auth", "auth.log")

auth_bp = Blueprint("auth", __name__)
user_service = UserService()

# ------------------- Default Admin Config ------------------- #
DEFAULT_ADMIN_USERNAME = os.getenv("KAGAPA_USERNAME", "kagapa")
DEFAULT_ADMIN_PASSWORD = os.getenv("KAGAPA_PASSWORD", "kagapa")
DEFAULT_ADMIN_PAYLOAD = {
    "name": "kagapa",
    "phone": "1233333423",
    "email": "kagapa@gmail.com",
    "username": DEFAULT_ADMIN_USERNAME,
    "password": DEFAULT_ADMIN_PASSWORD,
}


# ------------------- Cache Control ------------------- #
@auth_bp.after_app_request
def add_cache_control(response):
    """Prevent browser caching of protected pages."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# ------------------- Signup ------------------- #
@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Register a new user."""
    try:
        data = request.get_json()
        if not data or not all(data.values()):
            return jsonify({"error": "ಎಲ್ಲಾ ಸ್ಥಳಗಳನ್ನು ಪೂರೈಸಿ."}), 400

        new_user = user_service.create_user(**data)
        logger.info(f"User '{new_user.username}' created successfully")
        return jsonify({"message": "ಬಳಕೆದಾರರನ್ನು ಯಶಸ್ವಿಯಾಗಿ ರಚಿಸಲಾಗಿದೆ."}), 201

    except ValueError as e:
        logger.warning(f"Signup failed: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# ------------------- Admin Creation ------------------- #
@auth_bp.route("/admin/create", methods=["POST"])
@admin_required
def create_admin_route():
    """Create a new admin."""
    try:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        if not username or not email:
            return jsonify({"error": "Username and Email are required."}), 400

        admin = user_service.create_admin(username=username, email=email)
        logger.info(f"Admin '{username}' created successfully")
        return jsonify({"message": "Admin created successfully."}), 201

    except ValueError as e:
        logger.warning(f"Admin creation failed: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error during admin creation: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# ------------------- Login ------------------- #
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        logger.info("Login page rendered")
        return render_template("login.html")
    try:
       result =  user_service.create_default_admin(payload=DEFAULT_ADMIN_PAYLOAD)
       logger.info(result)
       print(result)
    except Exception as e:
        print(e)

    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        logger.info(f"Login attempt for username: {username}")

        # Authenticate user via UserService
        user = user_service.verify_user_credentials(username, password)
        if not user:
            logger.warning(f"Failed login attempt for user: {username}")
            return jsonify({"error": "Invalid username or password"}), 401

        # Check if admin
        is_admin = user_service.is_admin(user.id)
        user_type = "admin" if is_admin else "user"

        # Generate JWT
        token = user_service.generate_jwt_token(user, user_type)

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
            secure=False  # True in production with HTTPS
        )

        logger.info(f"{user_type.capitalize()} '{username}' logged in successfully")
        return response

    except Exception as e:
        logger.exception(f"Unexpected error during login: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# ------------------- Logout ------------------- #
@auth_bp.route("/logout", methods=["GET"])
def logout():
    """Clear the JWT cookie."""
    response = make_response(jsonify({"message": "Logged out successfully"}))
    response.set_cookie("access_token", "", expires=0)
    logger.info("User logged out and token cleared")
    return response


# ------------------- Current User Info ------------------- #
@auth_bp.route("/me", methods=["GET"])
def me():
    access_token = request.cookies.get("access_token")
    if not access_token:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        payload = user_service.decode_jwt_token(access_token)
        return jsonify({
            "user_id": payload["user_id"],
            "username": payload["username"],
            "user_type": payload["user_type"],
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
