import os
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

import jwt
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt

from app.config.database import db_instance
from app.models.user_management import User, Admin
from app.utils.logger import setup_logger

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in environment variables")


class UserService:
    def __init__(self):
        self.bcrypt = Bcrypt()
        self.logger = setup_logger(name='user_service')

    # ----------------------
    # CREATE
    # ----------------------
    def create_user(self, name: str, phone: str, email: str, username: str, password: str) -> User:
        """Create a new user with hashed password."""
        if User.query.filter((User.email == email) | (User.username == username)).first():
            raise ValueError("Email or username already exists.")

        hashed_password = self.bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(
            name=name,
            phone=phone,
            email=email,
            username=username,
            password_hash=hashed_password,
            created_at=datetime.now(timezone.utc),
        )
        db_instance.session.add(new_user)
        db_instance.session.commit()
        return new_user

    def create_admin(self, username: str, email: str) -> Admin:
        """Create a new admin entry."""
        if Admin.query.filter((Admin.email == email) | (Admin.username == username)).first():
            raise ValueError("Admin with this email or username already exists.")

        new_admin = Admin(
            username=username,
            email=email,
            created_at=datetime.now(timezone.utc),
        )
        db_instance.session.add(new_admin)
        db_instance.session.commit()
        return new_admin

    def create_default_admin(self, payload: dict) -> dict:
        """
        Ensure a user exists and is marked as admin.
        1. Check Admin table first.
        2. If not found, create User if missing.
        3. Create Admin entry.
        """
        try:
            username = payload.get("username")
            email = payload.get("email")
            password = payload.get("password")
            name = payload.get("name")
            phone = payload.get("phone")

            if not all([username, email, password, name]):
                return {
                    "status": "error",
                    "message": "Missing required fields: name, email, username, password",
                    "user_id": None,
                }

            # Step 1: Already admin?
            admin_entry = Admin.query.filter_by(username=username).first()
            if admin_entry:
                return {
                    "status": "exists",
                    "message": f"User '{username}' already exists as an admin.",
                    "user_id": None,
                }

            # Step 2: Ensure user exists
            user = User.query.filter(
                (User.email == email) | (User.username == username)
            ).first()

            user_created = False
            if not user:
                hashed_password = self.bcrypt.generate_password_hash(password).decode("utf-8")
                user = User(
                    name=name,
                    phone=phone,
                    email=email,
                    username=username,
                    password_hash=hashed_password,
                    created_at=datetime.now(timezone.utc),
                )
                db_instance.session.add(user)
                db_instance.session.commit()
                user_created = True

            # Step 3: Add to admin table
            new_admin = Admin(
                username=user.username,
                email=user.email,
                created_at=datetime.now(timezone.utc),
            )
            db_instance.session.add(new_admin)
            db_instance.session.commit()

            message = (
                f"User '{username}' created and promoted to admin."
                if user_created
                else f"User '{username}' already existed and promoted to admin."
            )

            return {"status": "success", "message": message, "user_id": user.id}

        except Exception as e:
            db_instance.session.rollback()
            return {
                "status": "error",
                "message": f"Failed to create user/admin: {str(e)}",
                "user_id": None,
            }

    def is_admin(self, user_id: int) -> bool:
        """Check if a user is an admin by username."""
        user = User.query.get(user_id)
        if not user:
            return False
        admin_entry = Admin.query.filter_by(username=user.username).first()
        return admin_entry is not None

    # ----------------------
    # READ
    # ----------------------
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Fetch a user by ID."""
        return User.query.get(user_id)

    def get_all_users_with_admin_status(self) -> List[Dict[str, Any]]:
        """Return all users with admin flag."""
        users = User.query.all()
        admin_usernames = {admin.username for admin in Admin.query.all()}
        return [
            {
                "id": user.id,
                "username": user.username,
                "phone": user.phone,
                "email": user.email,
                "is_admin": user.username in admin_usernames,
            }
            for user in users
        ]

    # ----------------------
    # UPDATE
    # ----------------------
    def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        is_admin: Optional[bool] = None,
    ) -> User:
        """Update user details and optionally admin status."""
        user = User.query.get_or_404(user_id)

        if username:
            user.username = username
        if email is not None:
            user.email = email
        if phone is not None:
            user.phone = phone

        if is_admin is not None:
            self.update_admin_status(user_id, is_admin)

        db_instance.session.commit()
        return user

    def update_admin_status(self, user_id: int, is_admin: bool) -> bool:
        """Add or remove a user from Admin table."""
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
    def delete_user(self, user_id: int) -> bool:
        """Delete a user and remove admin entry if exists."""
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
    def verify_user_credentials(self, username: str, password: str) -> Optional[User]:
        """Verify username & password."""
        user = User.query.filter_by(username=username).first()
        if not user or not self.bcrypt.check_password_hash(user.password_hash, password):
            return None
        return user

    def generate_jwt_token(self, user: User, user_type: str, expires_in: int = 30) -> str:
        """Generate JWT token for a user."""
        payload = {
            "user_id": user.id,
            "username": user.username,
            "user_type": user_type,
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=expires_in)).timestamp()),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def decode_jwt_token(self, token: str) -> dict:
        """Decode and validate JWT."""
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired.")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token.")

    # ----------------------
    # PASSWORD RESET
    # ----------------------
    def reset_user_password(self, user_id: int, new_password: str) -> bool:
        """Reset a user's password securely."""
        if not new_password or len(new_password) < 6:
            raise ValueError("Password must be at least 6 characters long.")

        user = User.query.get_or_404(user_id)
        user.set_password(new_password, self.bcrypt)

        if hasattr(user, "password_reset_at"):
            user.password_reset_at = datetime.now(timezone.utc)

        db_instance.session.commit()
        return True
