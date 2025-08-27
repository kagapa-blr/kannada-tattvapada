import os
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate, init as migrate_init, migrate as flask_migrate, upgrade
from app.config.database import db_instance, init_db
from app.routes.admin_routes import admin_bp
from app.routes.auth_routes import auth_bp
from app.routes.delete_tatvapada import delete_bp
from app.routes.document_routes import documents_bp
from app.routes.error_handling import errors_bp
from app.routes.home import home_bp
from app.routes.right_section_ui import right_section_bp
from app.routes.right_section_api import right_section_impl_bp
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

# -------------------- Step 6b: Flask-Migrate Setup -------------------- #
migrate = Migrate(app, db_instance)
logger.info("Flask-Migrate initialized.")

# -------------------- Step 7: Blueprint Registration -------------------- #
app.register_blueprint(home_bp)
app.register_blueprint(tatvapada_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(delete_bp)
app.register_blueprint(documents_bp)
app.register_blueprint(errors_bp)
app.register_blueprint(right_section_bp)
app.register_blueprint(right_section_impl_bp)

logger.info(
    "Blueprints registered: home_bp, tatvapada_bp, auth_bp, admin_bp, delete_bp, documents_bp, errors_bp, right_section_bp, right_section_impl_bp"
)

# -------------------- Step 8: Fully Automatic Migrations -------------------- #
def auto_upgrade():
    """Automatically generate migration scripts and apply pending migrations."""
    migrations_path = os.path.join(app_root, "migrations")

    # 1️ Initialize migrations folder if missing
    if not os.path.exists(migrations_path):
        logger.info("Migrations folder not found. Initializing...")
        migrate_init(directory=migrations_path)
        logger.info("Migrations folder created.")

    # 2️ Autogenerate a migration script for any changes
    logger.info("Autogenerating migration script for model changes...")
    flask_migrate(directory=migrations_path, message="Auto migration")
    logger.info("Migration script generated.")

    # 3️ Apply all migrations
    logger.info("Applying pending database migrations...")
    upgrade(directory=migrations_path)
    logger.info("Database migrations applied successfully.")

# -------------------- Step 9: Entry Point -------------------- #
if __name__ == "__main__":
    logger.info("Launching Tatvapada Flask app...")

    with app.app_context():
        auto_upgrade()

        # Print the current tables
        inspector = db_instance.inspect(db_instance.engine)
        tables = inspector.get_table_names()
        logger.info(f"Tables in the database: {tables}")
        print("Created/updated tables:", tables)

    logger.info("Flask app is up and running")
    app.run(host="0.0.0.0", port=5000, debug=False)
