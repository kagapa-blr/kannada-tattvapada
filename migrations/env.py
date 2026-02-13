import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Add project root to path
# --------------------------------------------------
sys.path.append(os.getcwd())

# --------------------------------------------------
# Import Flask-SQLAlchemy db instance
# --------------------------------------------------
from app.config.database import db_instance
import app.models  # IMPORTANT: ensures all models are registered

# --------------------------------------------------
# Alembic Config
# --------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --------------------------------------------------
# Build MySQL connection string from .env
# --------------------------------------------------
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

config.set_main_option("sqlalchemy.url", DATABASE_URL)

# --------------------------------------------------
# Set metadata for autogenerate
# --------------------------------------------------
target_metadata = db_instance.metadata


# --------------------------------------------------
# Offline migrations
# --------------------------------------------------
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# --------------------------------------------------
# Online migrations
# --------------------------------------------------
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# --------------------------------------------------
# Run
# --------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
