from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime

from app.config.database import db_instance


class User(db_instance.Model):
    """
    Stores user login and registration details.
    """
    __tablename__ = "users"
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci'
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100, collation='utf8mb4_general_ci'), nullable=False)
    phone = Column(String(15, collation='utf8mb4_general_ci'), nullable=True)
    email = Column(String(120, collation='utf8mb4_general_ci'), unique=True, nullable=False)
    username = Column(String(50, collation='utf8mb4_general_ci'), unique=True, nullable=False)
    password_hash = Column(String(255, collation='utf8mb4_general_ci'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def set_password(self, raw_password, bcrypt):
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode('utf-8')

    def check_password(self, raw_password, bcrypt):
        return bcrypt.check_password_hash(self.password_hash, raw_password)

class Admin(db_instance.Model):
    """
    Stores admin login details.
    """
    __tablename__ = "admins"
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_general_ci'
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50, collation='utf8mb4_general_ci'), unique=True, nullable=False)
    email = Column(String(120, collation='utf8mb4_general_ci'), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
