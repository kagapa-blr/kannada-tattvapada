import os
import shutil

from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import create_engine, text, inspect
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

MIGRATIONS_DIR = "migrations/versions"


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


def list_tables():
    """List all tables in the database."""
    engine = create_engine(DATABASE_URI)
    insp = inspect(engine)
    return insp.get_table_names()


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

    # Ask reset mode
    mode = input("\nDo you want to:\n"
                 "1. Reset specific table(s)\n"
                 "2. Full reset (drop & recreate DB)\n"
                 "Enter choice (1 or 2): ").strip()

    if mode == "2":
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

    elif mode == "1":
        # Step 1: List tables
        try:
            tables = list_tables()
        except Exception as e:
            logger.error(f"Could not fetch tables: {e}")
            return

        if not tables:
            print("No tables found in database.")
            return

        print("\nTables in database:")
        for idx, tbl in enumerate(tables, start=1):
            print(f"{idx}. {tbl}")
        print(f"{len(tables)+1}. All (reset all tables)")

        table_choice = input("Select table(s) to reset (comma separated numbers): ").strip()
        selected = [x.strip() for x in table_choice.split(",")]

        engine = create_engine(DATABASE_URI)
        with engine.connect() as conn:
            if str(len(tables)+1) in selected:
                # Drop all tables
                for tbl in tables:
                    try:
                        conn.execute(text(f"DROP TABLE IF EXISTS `{tbl}`;"))
                        logger.info(f"Dropped table {tbl}")
                    except Exception as e:
                        logger.error(f"Failed to drop table {tbl}: {e}")
            else:
                for idx in selected:
                    try:
                        tbl = tables[int(idx)-1]
                        conn.execute(text(f"DROP TABLE IF EXISTS `{tbl}`;"))
                        logger.info(f"Dropped table {tbl}")
                    except Exception as e:
                        logger.error(f"Failed to drop table: {e}")
                        continue

        # Step 2: Recreate dropped tables from models
        app = init_app()
        with app.app_context():
            db_instance.create_all()
            logger.info("Selected table(s) recreated successfully from models.")
        print("Table(s) reset successfully.")
    else:
        print("Invalid option selected.")


def main():
    print("\nSelect an operation:")
    print("1. Reset database (table-level or full DB)")
    choice = input("Enter your choice (1): ").strip()
    logger.debug(f"User selected option: {choice}")

    if choice == "1":
        reset_database()
    else:
        print("Invalid option selected.")


if __name__ == "__main__":
    main()
