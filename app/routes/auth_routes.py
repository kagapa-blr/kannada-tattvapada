import os

from dotenv import load_dotenv
from flask import (
    Blueprint, request, render_template, make_response, jsonify
)
from flask import redirect, url_for

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

        # ✅ Redirect to login page after successful signup
        return redirect(url_for("auth.login"))

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
# ------------------- Login ------------------- #
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # ----------------------------
    # Check if user is already logged in
    # ----------------------------
    token = request.cookies.get("access_token")
    if token and not user_service.is_jwt_expired(token):
        try:
            user_data = user_service.decode_jwt_token(token)
            if user_data:
                return redirect(url_for("home.home_page"))  # ✅ redirect to home_bp
        except ValueError:
            pass  # Token invalid, allow login

    if request.method == "GET":
        return render_template("login.html")

    # ----------------------------
    # POST login request
    # ----------------------------
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid request"}), 400

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "success": False,
                "message": "Username and password are required"
            }), 400

        user = user_service.verify_user_credentials(identifier=username.strip(), password=password.strip())
        if not user:
            return jsonify({
                "success": False,
                "message": "User not found or incorrect password"
            }), 404

        user_type = "admin" if user_service.is_admin(user.id) else "user"
        token = user_service.generate_jwt_token(user, user_type)

        response = make_response(jsonify({
            "success": True,
            "message": "Login successful",
            "token": token,
            "username": username,
            "user_type": user_type
        }))

        response.set_cookie(
            "access_token",
            token,
            httponly=True,
            secure=True,       # ⚠️ Use False for local dev without HTTPS
            samesite="Strict",
            max_age=60 * 60 * 24 * 7  # 7 days
        )

        return response

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Internal server error: {str(e)}"
        }), 500

# ------------------- Logout ------------------- #
@auth_bp.route("/logout", methods=["GET"])
def logout():
    """Clear the JWT cookie and redirect to login page."""
    response = make_response(redirect(url_for("auth.login")))  # Redirect to login route
    response.set_cookie("access_token", "", expires=0)  # Clear cookie
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
        user_email = user_service.get_user_by_id(payload["user_id"])
        return jsonify({
            "user_id": payload["user_id"],
            "username": payload["username"],
            "user_type": payload["user_type"],
            "user_email":user_email.email
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
