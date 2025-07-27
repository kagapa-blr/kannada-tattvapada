"""
Home route for displaying Tatvapada records in the main view.
"""

from flask import Blueprint, render_template
from app.models.tatvapada import Tatvapada
from app.config.database import db_instance
from app.utils.logger import setup_logger

# Set up logger for this module
logger = setup_logger("home", "home.log")

# Create a Blueprint for home
home_bp = Blueprint("home", __name__)

@home_bp.route('/')
def home_page():
    """
    Home route handler.
    - Checks if any Tatvapada records exist.
    - If not, inserts a default sample record.
    - Then fetches and renders all records in the template.
    """
    logger.info("Processing request for home page...")

    try:
        # Insert sample if DB is empty
        if not Tatvapada.query.first():
            logger.info("No records found. Inserting sample Tatvapada record...")

            sample = Tatvapada(
                tatvapadakosha="ಕರ್ನಾಟಕ ಸಮಗ್ರ ತತ್ವಪದಗಳ ಜನಪ್ರಿಯ ಸಂಪುಟ ಮಾಲೆ",
                tatvapadakosha_sankhye=1,
                samputa_sankhye=2,
                tatvapadakosha_sheershike="ಶಿಶುನಾಳ ಶರೀಫರ ತತ್ವಪದಗಳುಶಿಶುನಾಳ ಶರೀಫ",
                tatvapadakarara_hesaru="ಶಿಷುನಾಳ ಶರೀಫ಼",
                mukhya_sheershike="ದೇವಸ್ತುತಿ",
                tatvapada_sankhye="೧",
                tatvapada_hesaru="ಪಾಲಿಸಯ್ಯ ಪಾರ್ವತೀಪತಿ",
                tatvapada=(
                    "ಪಾಲಿಸಯ್ಯ ಪಾರ್ವತೀಪತಿ \n"
                    "ತ್ರಿಲೋಕದೋಳ್ ವಿರತಿ\t|| ಪ ||\n\n"
                    "ಗಂಗಾಧರನ ಸ್ತುತಿ \n"
                    "ಧ್ಯಾನಿಸುವ ಆತ್ಮಾಭಿರತಿ\n"
                    "ಕರುಣಿ ಕೈಲಾಸಕಧಿಪತಿ\t|| 1 ||\n\n"
                    "ಗಿರಿಜಾ ರಮಣನ ಸ್ತುತಿ\n"
                    "ಭಜಿಸಿ ಶಿವಯೋಗ ಸ್ಥಿತಿ\n"
                    "ಸಿದ್ದ ಶಿವಯೋಗಿ ಸುಮತಿ\t|| 2 ||\n\n"
                    "ಬೇಗನೆ ಹೊಂದಿಸು ಸದ್ಗತಿ\n"
                    "ಶಿಶುನಾಳಧೀಶನೇ ಗತಿ\n"
                    "ಕೊಡು ಬೇಗನೆ ಮುಕುತಿ\t|| 3 ||"
                ),
                klishta_padagalu_artha=None,
                tippani=None
            )
            db_instance.session.add(sample)
            db_instance.session.commit()
            logger.info("Sample Tatvapada record inserted.")

        # Fetch all Tatvapada records
        records = Tatvapada.query.all()
        logger.info(f"Fetched {len(records)} Tatvapada records.")

        return render_template("index.html", data=records)

    except Exception as e:
        logger.error(f"An error occurred while processing home page: {e}")
        return render_template("index.html", data=[])


@home_bp.route('/old')
def home_old():
    return render_template("old.html")
