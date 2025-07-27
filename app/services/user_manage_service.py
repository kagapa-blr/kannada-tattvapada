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

def create_user(name, phone, email, username, password):
    """
    Creates a new user with a hashed password.
    """
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
    """
    Creates a new admin.
    """
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

def verify_user_credentials(username, password):
    """
    Verifies username and password. Returns user if valid.
    """
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return None
    return user

def generate_jwt_token(user):
    """
    Generates a JWT token for a given user.
    """
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    # PyJWT expects 'exp' to be a Unix timestamp, not a datetime object.
    payload["exp"] = int(payload["exp"].timestamp())
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_jwt_token(token):
    """
    Decodes and validates a JWT token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token.")

def get_user_by_id(user_id):
    """
    Retrieves a user object by user ID.
    """
    return User.query.get(user_id)
