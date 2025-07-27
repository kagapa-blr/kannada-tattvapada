# app/utils/auth_decorator.py

from functools import wraps
from flask import request, redirect, url_for, flash
from app.services.user_manage_service import decode_jwt_token


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            flash("ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಆಗಿ.", "warning")
            return redirect(url_for("auth.login"))
        try:
            payload = decode_jwt_token(token)

            # You can attach user info to flask.g if needed here
        except Exception as e:
            flash(str(e), "danger")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapper
