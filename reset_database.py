import os
import shutil

from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

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


def list_tables():
    engine = create_engine(DATABASE_URI)
    insp = inspect(engine)
    return insp.get_table_names()


def reset_database():
    print_db_config()
    print("\nWarning: Make sure the application is not running before continuing.")
    proceed = input("Have you stopped the application? (yes/no): ").strip().lower()

    if proceed not in ["yes", "y"]:
        print("Operation aborted. Please stop the app and try again.")
        return

    success, error = test_db_connection()
    if not success:
        logger.error(f"Database connection failed: {error}")
        return

    mode = input(
        "\nDo you want to:\n"
        "1. Reset specific table(s)\n"
        "2. Full reset (drop database)\n"
        "Enter choice (1 or 2): "
    ).strip()

    # --------------------------------------------------
    # FULL RESET (Drop Database Only)
    # --------------------------------------------------
    if mode == "2":
        confirm = input(
            f"\nConnection successful.\n"
            f"Do you want to DROP the database '{DB_NAME}' and delete all migrations? (yes/no): "
        ).strip().lower()

        if confirm not in ["yes", "y"]:
            print("Operation cancelled.")
            return

        # Delete migrations folder
        if os.path.exists(MIGRATIONS_DIR):
            try:
                shutil.rmtree(MIGRATIONS_DIR)
                logger.info(f"Deleted migrations directory: {MIGRATIONS_DIR}")
            except Exception as e:
                logger.error(f"Failed to delete migrations directory: {e}")
                return

        # Drop database
        try:
            engine = create_engine(ROOT_URI)
            with engine.connect() as conn:
                conn.execute(text(f"DROP DATABASE IF EXISTS `{DB_NAME}`;"))
            logger.info(f"Database '{DB_NAME}' dropped successfully.")
            print("Database dropped successfully.")
        except SQLAlchemyError as e:
            logger.error(f"Error during database drop: {e}")
            return

    # --------------------------------------------------
    # TABLE RESET (Drop Tables Only)
    # --------------------------------------------------
    elif mode == "1":
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
        print(f"{len(tables)+1}. All (drop all tables)")

        table_choice = input("Select table(s) to drop (comma separated numbers): ").strip()
        selected = [x.strip() for x in table_choice.split(",")]

        engine = create_engine(DATABASE_URI)
        with engine.connect() as conn:

            if str(len(tables) + 1) in selected:
                for tbl in tables:
                    try:
                        conn.execute(text(f"DROP TABLE IF EXISTS `{tbl}`;"))
                        logger.info(f"Dropped table {tbl}")
                    except Exception as e:
                        logger.error(f"Failed to drop table {tbl}: {e}")
            else:
                for idx in selected:
                    try:
                        tbl = tables[int(idx) - 1]
                        conn.execute(text(f"DROP TABLE IF EXISTS `{tbl}`;"))
                        logger.info(f"Dropped table {tbl}")
                    except Exception as e:
                        logger.error(f"Failed to drop table: {e}")

        print("Selected table(s) dropped successfully.")

    else:
        print("Invalid option selected.")


def main():
    print("\nSelect an operation:")
    print("1. Reset database (table-level or full DB)")
    choice = input("Enter your choice (1): ").strip()

    if choice == "1":
        reset_database()
    else:
        print("Invalid option selected.")


if __name__ == "__main__":
    main()
