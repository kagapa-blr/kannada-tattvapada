import os
import sys
from flask import Flask
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from flask_migrate import Migrate, upgrade, init, migrate

from app.config.database import db_instance
from app.utils.logger import setup_logger

# Initialize logger
logger = setup_logger(name="reset_database", log_file="reset_database")

# Load environment variables
load_dotenv()

# Database config
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

# URIs
ROOT_URI = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"
DATABASE_URI = f"{ROOT_URI}{DB_NAME}?charset=utf8mb4"

MIGRATIONS_DIR = "migrations"


def print_db_config():
    logger.info("Database configuration:")
    logger.info(f"  Name     : {DB_NAME}")
    logger.info(f"  Host     : {DB_HOST}")
    logger.info(f"  Port     : {DB_PORT}")
    logger.info(f"  Username : {DB_USERNAME}")
    logger.info(f"  Password : [hidden]")


def test_db_connection():
    try:
        engine = create_engine(ROOT_URI)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except SQLAlchemyError as e:
        return False, str(e)


def init_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db_instance.init_app(app)
    return app


def reset_database():
    print_db_config()
    print("\nWarning: Make sure the application is not running before continuing.")
    proceed = input("Have you stopped the application? (yes/no): ").strip().lower()
    logger.debug(f"User input for application stop confirmation: {proceed}")

    if proceed not in ["yes", "y"]:
        print("Operation aborted. Please stop the app and try again.")
        return

    success, error = test_db_connection()
    if not success:
        logger.error(f"Database connection failed: {error}")
        return

    confirm = input(f"\nConnection successful.\nDo you want to DROP and RECREATE the database '{DB_NAME}'? (yes/no): ").strip().lower()
    logger.debug(f"User input for drop/create confirmation: {confirm}")

    if confirm not in ["yes", "y"]:
        print("Operation cancelled.")
        return

    try:
        engine = create_engine(ROOT_URI)
        with engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS `{DB_NAME}`;"))
            conn.execute(text(f"CREATE DATABASE `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
        logger.info(f"Database '{DB_NAME}' dropped and recreated.")
    except SQLAlchemyError as e:
        logger.error(f"Error during database reset: {e}")
        return

    app = init_app()
    with app.app_context():
        db_instance.create_all()
        logger.info("Tables created successfully from models.")


def repair_database():
    print_db_config()
    logger.info("Applying Flask-Migrate migrations...")

    app = init_app()
    migrate_obj = Migrate(app, db_instance, directory=MIGRATIONS_DIR)

    with app.app_context():
        try:
            if not os.path.exists(MIGRATIONS_DIR):
                logger.info("Migrations directory not found. Initializing migrations...")
                init(directory=MIGRATIONS_DIR)
                logger.info("Migrations initialized.")

            logger.info("Autogenerating migration script...")
            migrate(message="Auto migration")
            logger.info("Migration script generated.")

            upgrade()
            logger.info("Database schema upgraded using migrations.")

        except Exception as e:
            logger.error("Flask-Migrate failed during migration.")
            logger.error(str(e))


def main():
    print("\nSelect an operation:")
    print("1. Reset database (drop and recreate)")
    print("2. Repair database (apply migrations)")
    choice = input("Enter your choice (1 or 2): ").strip()
    logger.debug(f"User selected option: {choice}")

    if choice == "1":
        reset_database()
    elif choice == "2":
        repair_database()
    else:
        print("Invalid option selected.")


if __name__ == "__main__":
    main()
