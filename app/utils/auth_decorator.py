# app/utils/auth_decorator.py
from functools import wraps
from flask import g, jsonify, request, redirect, url_for, flash

from app.services.user_manage_service import UserService
from app.utils.logger import setup_logger

logger = setup_logger("auth_decorator", )

user_service = UserService()
def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            flash("ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಆಗಿ.", "warning")
            logger.warning("Login required but no token found")
            return redirect(url_for("auth.login"))
        try:
            payload = user_service.decode_jwt_token(token)
            g.user = user_service.get_user_by_id(payload.get("user_id"))
            if not g.user:
                logger.warning("Token valid but user not found in DB")
                return redirect(url_for("auth.login"))
        except Exception as e:
            flash(str(e), "danger")
            logger.error(f"Login check failed: {str(e)}")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapper


def admin_required(route_function):
    """
    Decorator to ensure the user is logged in and has admin privileges.
    Special case: user 'kagapa' is always allowed.
    """

    @wraps(route_function)
    def wrapper(*args, **kwargs):
        access_token = request.cookies.get("access_token")
        if not access_token:
            logger.warning("Admin access denied: no token")
            return redirect(url_for("auth.login"))

        try:
            token_payload = user_service.decode_jwt_token(access_token)
            user_id = token_payload.get("user_id")
            current_user = user_service.get_user_by_id(user_id)
            if not current_user:
                logger.info("Admin access denied: user not found")
                return redirect(url_for("auth.login"))

            g.user = current_user

            # Special bypass for username "kagapa"
            if g.user.username == "kagapa":
                logger.info("Special admin bypass granted for user 'kagapa'")
                return route_function(*args, **kwargs)

            # Normal admin check
            admin_users = {
                admin["username"]
                for admin in user_service.get_all_users_with_admin_status()
                if admin["is_admin"]
            }
            is_admin = g.user.username in admin_users

            if not is_admin:
                logger.warning(f"User '{g.user.username}' tried admin route without rights")
                return jsonify({"error": "Admin privileges required"}), 403

        except Exception as exc:
            logger.error(f"Admin check failed: {str(exc)}", exc_info=True)
            return redirect(url_for("auth.login"))

        return route_function(*args, **kwargs)

    return wrapper
