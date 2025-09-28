from datetime import datetime, timezone
from sqlalchemy import Boolean
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from app.config.database import db_instance
from sqlalchemy.dialects.mysql import JSON


class User(db_instance.Model):
    """
    Stores user login and registration details.
    """
    __tablename__ = "users"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100, collation='utf8mb4_unicode_ci'), nullable=False)
    phone = Column(String(15, collation='utf8mb4_unicode_ci'), nullable=True)
    email = Column(String(120, collation='utf8mb4_unicode_ci'), unique=True, nullable=False)
    username = Column(String(50, collation='utf8mb4_unicode_ci'), unique=True, nullable=False)
    password_hash = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def set_password(self, raw_password, bcrypt):
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode('utf-8')

    def check_password(self, raw_password, bcrypt):
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


class Admin(db_instance.Model):
    """
    Stores admin login details.
    """
    __tablename__ = "admins"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50, collation='utf8mb4_unicode_ci'), unique=True, nullable=False)
    email = Column(String(120, collation='utf8mb4_unicode_ci'), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Admin(id={self.id}, username='{self.username}')>"


class ShoppingUser(db_instance.Model):
    __tablename__ = "shopping_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    name_override = Column("name", String(100, collation='utf8mb4_unicode_ci'), nullable=True)
    phone_override = Column("phone", String(15, collation='utf8mb4_unicode_ci'), nullable=True)
    gender = Column(String(10), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    preferred_language = Column(String(20), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", backref="shopping_profile", uselist=False)
    addresses = relationship("ShoppingUserAddress", back_populates="shopping_user", cascade="all, delete-orphan")
    orders = relationship("ShoppingOrder", back_populates="shopping_user", cascade="all, delete-orphan")

    @hybrid_property
    def name(self):
        return self.name_override if self.name_override else (self.user.name if self.user else None)

    @hybrid_property
    def phone(self):
        return self.phone_override if self.phone_override else (self.user.phone if self.user else None)

    @hybrid_property
    def email(self):
        return self.user.email if self.user else None

    def __repr__(self):
        return f"<ShoppingUser(id={self.id}, name='{self.name}', email='{self.email}')>"


class ShoppingUserAddress(db_instance.Model):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shopping_user_id = Column(Integer, ForeignKey("shopping_users.id", ondelete="CASCADE"), nullable=False)
    address_line = Column(Text, nullable=False)
    city = Column(String(100), nullable=True)
    taluk_division = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    address_type = Column(String(20), nullable=True)
    is_default = Column(Boolean, default=False)
    recipient_name = Column(String(100), nullable=True)
    phone_number = Column(String(15), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    delivery_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    shopping_user = relationship("ShoppingUser", back_populates="addresses")

    def __repr__(self):
        return f"<Address(id={self.id}, type='{self.address_type}', city='{self.city}', postal_code='{self.postal_code}')>"

class ShoppingOrder(db_instance.Model):
    __tablename__ = "shopping_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shopping_user_id = Column(Integer, ForeignKey("shopping_users.id", ondelete="CASCADE"), nullable=False)
    order_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), nullable=False, default="Pending")
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=True)
    shipping_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=True)
    notes = Column(Text, nullable=True)

    # NEW columns to store extra info
    user_info = Column(JSON, nullable=True)
    address_info = Column(JSON, nullable=True)
    items = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    shopping_user = relationship("ShoppingUser", back_populates="orders")
    shipping_address = relationship("ShoppingUserAddress")
