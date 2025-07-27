import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate, upgrade, init, migrate
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.config.database import db_instance
from app.utils.logger import setup_logger

# Initialize logger
logger = setup_logger(name="reset_database", log_file="reset_database.log")

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


import shutil  # Add this at the top

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

    confirm = input(f"\nConnection successful.\nDo you want to DROP and RECREATE the database '{DB_NAME}' and delete all migrations? (yes/no): ").strip().lower()
    logger.debug(f"User input for drop/create confirmation: {confirm}")

    if confirm not in ["yes", "y"]:
        print("Operation cancelled.")
        return

    # Step 1: Delete migrations folder
    if os.path.exists(MIGRATIONS_DIR):
        try:
            shutil.rmtree(MIGRATIONS_DIR)
            logger.info(f"Deleted migrations directory: {MIGRATIONS_DIR}")
        except Exception as e:
            logger.error(f"Failed to delete migrations directory: {e}")
            return

    # Step 2: Drop and recreate database
    try:
        engine = create_engine(ROOT_URI)
        with engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS `{DB_NAME}`;"))
            conn.execute(text(f"CREATE DATABASE `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
        logger.info(f"Database '{DB_NAME}' dropped and recreated.")
    except SQLAlchemyError as e:
        logger.error(f"Error during database reset: {e}")
        return

    # Step 3: Re-initialize app and create tables
    app = init_app()
    with app.app_context():
        db_instance.create_all()
        logger.info("Tables created successfully from models.")

def repair_database():
    print_db_config()
    logger.info("Applying Flask-Migrate migrations...")

    app = init_app()
    Migrate(app, db_instance, directory=MIGRATIONS_DIR)

    with app.app_context():
        try:
            if not os.path.exists(MIGRATIONS_DIR):
                logger.info("Migrations directory not found. Initializing migrations...")
                init(directory=MIGRATIONS_DIR)
                logger.info("Migrations initialized.")

            # Step 1: Upgrade DB to latest migration
            logger.info("Upgrading to latest migration state...")
            upgrade()
            logger.info("Database upgraded to latest schema.")

            # Step 2: Allow user to generate new migration if needed
            generate_new = input("Do you want to generate a new migration script? (yes/no): ").strip().lower()
            if generate_new in ["yes", "y"]:
                migration_msg = input("Enter a migration message (default: 'Auto migration'): ").strip()
                if not migration_msg:
                    migration_msg = "Auto migration"

                logger.info(f"Autogenerating new migration script with message: {migration_msg}")
                migrate(message=migration_msg)
                logger.info("Migration script generated successfully.")
            else:
                print("Skipped migration generation.")

        except Exception as e:
            logger.error("Flask-Migrate failed during repair operation.")
            logger.exception(e)

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
