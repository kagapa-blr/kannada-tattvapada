import os
from flask import Flask
from dotenv import load_dotenv
from app.config.database import db_instance, init_db
from app.routes.admin_routes import admin_bp
from app.routes.auth_routes import auth_bp
from app.routes.home import home_bp
from app.routes.tatvapada import tatvapada_bp
from app.utils.logger import setup_logger

# -------------------- Step 1: Load Environment -------------------- #
load_dotenv()

# -------------------- Step 2: Logger Setup -------------------- #
logger = setup_logger("tatvapada", "extractor.log")
logger.info("Logger initialized.")

# -------------------- Step 3: Determine App Root & Template/Static Paths -------------------- #
app_root = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(app_root, "app", "templates")
static_path = os.path.join(app_root, "app", "static")

print("App root path:", app_root)
print("Template folder:", template_path)
print("Static folder:", static_path)

logger.info(f"App root path: {app_root}")
logger.info(f"Template folder path: {template_path}")
logger.info(f"Static folder path: {static_path}")

# -------------------- Step 4: App Initialization -------------------- #
app = Flask(__name__, static_folder=static_path, template_folder=template_path)
logger.info("Flask app instance created.")

# -------------------- Step 5: Configuration -------------------- #
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key")
logger.debug(f"SECRET_KEY loaded from environment: {app.config['SECRET_KEY']}")

# -------------------- Step 6: Database Initialization -------------------- #
init_db(app)
logger.info("Database initialized and SQLAlchemy bound to app.")

# -------------------- Step 7: Blueprint Registration -------------------- #
app.register_blueprint(home_bp)
app.register_blueprint(tatvapada_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")
logger.info("Blueprints registered: home_bp, tatvapada_bp, auth_bp, admin_bp")

# -------------------- Step 8: Entry Point -------------------- #
if __name__ == "__main__":
    logger.info("Launching Tatvapada Flask app...")

    with app.app_context():
        logger.debug("Creating tables if not present...")
        db_instance.create_all()
        logger.info("Database tables created or already exist.")

    logger.info("Flask app is up and running.")
    app.run(debug=False)
