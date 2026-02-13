from functools import wraps
from flask import g, jsonify, request, redirect, url_for, flash

from app.services.user_manage_service import UserService
from app.utils.logger import setup_logger

logger = setup_logger("auth_decorator")

user_service = UserService()


# ------------------------------------------------------------
# Helper: Extract token from Cookie OR Header
# ------------------------------------------------------------
def _extract_token():
    # 1. Try cookie
    token = request.cookies.get("access_token")
    if token:
        return token

    # 2. Try Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]

    return None


# ------------------------------------------------------------
# LOGIN REQUIRED
# ------------------------------------------------------------
def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):

        token = _extract_token()

        if not token:
            # API → return JSON
            if request.path.startswith("/api/"):
                return jsonify({
                    "error": "unauthorized",
                    "message": "Authentication token missing."
                }), 401

            # Web → redirect
            flash("ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಆಗಿ.", "warning")
            return redirect(url_for("auth.login"))

        try:
            payload = user_service.decode_jwt_token(token)
            user = user_service.get_user_by_id(payload.get("user_id"))

            if not user:
                raise Exception("User not found")

            g.user = user

        except Exception as e:
            logger.warning(f"Login check failed: {str(e)}")

            if request.path.startswith("/api/"):
                return jsonify({
                    "error": "invalid_token",
                    "message": "Invalid or expired token."
                }), 401

            flash("Session expired. Please login again.", "danger")
            return redirect(url_for("auth.login"))

        return view_func(*args, **kwargs)

    return wrapper


# ------------------------------------------------------------
# ADMIN REQUIRED
# ------------------------------------------------------------
def admin_required(route_function):

    @wraps(route_function)
    def wrapper(*args, **kwargs):

        token = _extract_token()

        if not token:
            if request.path.startswith("/api/"):
                return jsonify({
                    "error": "unauthorized",
                    "message": "Authentication token missing."
                }), 401

            return redirect(url_for("auth.login"))

        try:
            payload = user_service.decode_jwt_token(token)
            user_id = payload.get("user_id")

            if not user_id:
                raise Exception("Invalid token payload")

            current_user = user_service.get_user_by_id(user_id)

            if not current_user:
                raise Exception("User not found")

            g.user = current_user

            # Special bypass for kagapa
            if g.user.username == "kagapa":
                return route_function(*args, **kwargs)

            # Normal admin check
            admin_users = {
                admin["username"]
                for admin in user_service.get_all_users_with_admin_status()
                if admin.get("is_admin")
            }

            if g.user.username not in admin_users:
                return jsonify({
                    "error": "forbidden",
                    "message": "Admin privileges required."
                }), 403

            return route_function(*args, **kwargs)

        except Exception as exc:
            logger.error(f"Admin check failed: {str(exc)}", exc_info=True)

            return jsonify({
                "error": "invalid_token",
                "message": "Invalid or expired token."
            }), 401

    return wrapper
