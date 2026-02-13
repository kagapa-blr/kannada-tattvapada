import os

from dotenv import load_dotenv
from flask import Flask, send_from_directory

from app.config.database import db_instance, init_db
from app.routes.admin_routes import admin_bp
from app.routes.auth_routes import auth_bp
from app.routes.delete_tatvapada import delete_bp
from app.routes.document_routes import documents_bp
from app.routes.error_handling import errors_bp
from app.routes.home import home_bp
from app.routes.payment_routes import payment_bp
from app.routes.right_section_api import right_section_impl_bp
from app.routes.right_section_ui import right_section_bp
from app.routes.shopping_books_routes import shopping_books_bp
from app.routes.shopping_user_routes import shopping_user_bp
from app.routes.tatvapada import tatvapada_bp
from app.routes.tatvapadakarara_vivara import tatvapadakarara_bp
from app.services.user_manage_service import UserService
from app.utils.logger import setup_logger

# -------------------- Step 1: Load Environment -------------------- #
load_dotenv()

# ------------------- Default Admin Config ------------------- #
DEFAULT_ADMIN_USERNAME = os.getenv("KAGAPA_USERNAME", "kagapa")
DEFAULT_ADMIN_PASSWORD = os.getenv("KAGAPA_PASSWORD", "kagapa")
DEFAULT_ADMIN_PAYLOAD = {
    "name": "kagapa",
    "phone": "1233333423",
    "email": "kagapa@gmail.com",
    "username": DEFAULT_ADMIN_USERNAME,
    "password": DEFAULT_ADMIN_PASSWORD,
}

# -------------------- Step 2: Logger Setup -------------------- #
logger = setup_logger("main", "main.log")
logger.info("Logger initialized.\n")

# -------------------- Step 3: Determine App Root & Template/Static Paths -------------------- #
app_root = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(app_root, "app", "templates")
static_path = os.path.join(app_root, "app", "static")

logger.info(f"App root path: {app_root}")
logger.info(f"Template folder path: {template_path}")
logger.info(f"Static folder path: {static_path}")

# -------------------- Step 4: App Initialization -------------------- #
app = Flask(__name__, static_folder=static_path, template_folder=template_path)
logger.info("Flask app instance created.\n")

# -------------------- Step 5: Configuration -------------------- #
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key")

# -------------------- Step 6: Database Initialization -------------------- #
init_db(app)
logger.info("Database initialized and SQLAlchemy bound to app.")

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
app.register_blueprint(tatvapadakarara_bp)
app.register_blueprint(shopping_user_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(shopping_books_bp)

UPLOAD_FOLDER = os.path.join(app_root, "uploads")


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# -------------------- Step 8: Entry Point -------------------- #
if __name__ == "__main__":
    logger.info("Launching Tatvapada Flask app...\n")

    with app.app_context():

        # Print current tables
        inspector = db_instance.inspect(db_instance.engine)
        tables = inspector.get_table_names()
        logger.info(f"Tables in the database: {tables}")

        # Create default admin if not exists
        user_service = UserService()
        result = user_service.create_default_admin()
        logger.info(f"default user creation : {result}")
        print(f"default user creation : {result}")

        if tables:
            tables_list = "\n".join(
                [f"  {i + 1}. {table}" for i, table in enumerate(tables)]
            )
            logger.info(f"Tables in the database:\n{tables_list}\n")
        else:
            logger.info("No tables found in the database.\n")

    logger.info("Flask app is up and running\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
