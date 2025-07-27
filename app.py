# app.py

import os
from flask import Flask
from dotenv import load_dotenv
from app.config.database import db_instance, init_db
from app.routes.admin_routes import admin_bp
from app.routes.auth_routes import auth_bp
from app.routes.home import home_bp
from app.routes.tatvapada import tatvapada_bp
from app.utils.logger import setup_logger

# -------------------- Load Environment -------------------- #
load_dotenv()

# -------------------- Logger Setup -------------------- #
logger = setup_logger("tatvapada", "extractor.log")

# -------------------- Flask App Factory -------------------- #
def create_app() -> Flask:
    """Factory function to create and configure the Flask application."""
    logger.info("Initializing Flask application...")

    app = Flask(
        __name__,
        template_folder="app/templates",
        static_folder="app/static"
    )

    # ----------------- Configuration ----------------- #
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key")
    logger.debug(f"SECRET_KEY loaded from environment: {app.config['SECRET_KEY']}")

    # ----------------- Database Init ----------------- #
    init_db(app)
    logger.info("Database initialized and SQLAlchemy bound to app.")

    # ----------------- Blueprint Registration ----------------- #
    app.register_blueprint(home_bp)
    app.register_blueprint(tatvapada_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    logger.info("Blueprints registered: home_bp, tatvapada_bp")

    return app


# -------------------- Entry Point -------------------- #
if __name__ == "__main__":
    logger.info("Launching Tatvapada Flask app...")

    app = create_app()

    with app.app_context():
        logger.debug("Creating tables if not present...")
        db_instance.create_all()
        logger.info("Database tables created or already exist.")

    logger.info("Flask app is up and running.")
    app.run(debug=False)
