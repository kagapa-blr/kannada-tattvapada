# app/services/user_service.py

import os
from datetime import datetime, timezone, timedelta
import jwt
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from app.config.database import db_instance
from app.models.user_management import User, Admin

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in environment variables")

bcrypt = Bcrypt()

# ----------------------
# CREATE
# ----------------------
def create_user(name, phone, email, username, password):
    if User.query.filter((User.email == email) | (User.username == username)).first():
        raise ValueError("Email or username already exists.")

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = User(
        name=name,
        phone=phone,
        email=email,
        username=username,
        password_hash=hashed_password,
        created_at=datetime.now(timezone.utc)
    )
    db_instance.session.add(new_user)
    db_instance.session.commit()
    return new_user


def create_admin(username, email):
    if Admin.query.filter((Admin.email == email) | (Admin.username == username)).first():
        raise ValueError("Admin with this email or username already exists.")

    new_admin = Admin(
        username=username,
        email=email,
        created_at=datetime.now(timezone.utc)
    )
    db_instance.session.add(new_admin)
    db_instance.session.commit()
    return new_admin

# ----------------------
# READ
# ----------------------
def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_all_users_with_admin_status():
    users = User.query.all()
    admin_usernames = {admin.username for admin in Admin.query.all()}
    return [
        {
            "id": user.id,
            "username": user.username,
            "phone": user.phone,
            "email": user.email,
            "is_admin": user.username in admin_usernames
        }
        for user in users
    ]

# ----------------------
# UPDATE
# ----------------------
def update_user(user_id, username=None, email=None, phone=None, is_admin=None):
    user = User.query.get_or_404(user_id)

    if username:
        user.username = username
    if email is not None:
        user.email = email
    if phone is not None:
        user.phone = phone

    if is_admin is not None:
        admin_entry = Admin.query.filter_by(username=user.username).first()
        if is_admin:
            if not admin_entry:
                new_admin = Admin(username=user.username, email=user.email)
                db_instance.session.add(new_admin)
        else:
            if admin_entry:
                db_instance.session.delete(admin_entry)

    db_instance.session.commit()
    return user

def update_admin_status(user_id, is_admin):
    user = User.query.get_or_404(user_id)
    admin_entry = Admin.query.filter_by(username=user.username).first()

    if is_admin:
        if not admin_entry:
            new_admin = Admin(username=user.username, email=user.email)
            db_instance.session.add(new_admin)
    else:
        if admin_entry:
            db_instance.session.delete(admin_entry)

    db_instance.session.commit()
    return is_admin

# ----------------------
# DELETE
# ----------------------
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    admin_entry = Admin.query.filter_by(username=user.username).first()
    if admin_entry:
        db_instance.session.delete(admin_entry)

    db_instance.session.delete(user)
    db_instance.session.commit()
    return True

# ----------------------
# AUTH
# ----------------------
def verify_user_credentials(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return None
    return user

def generate_jwt_token(user):
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp())
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token.")
