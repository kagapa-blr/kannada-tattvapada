"""
Home route for displaying Tatvapada records in the main view.
"""

from flask import Blueprint, render_template

from app.utils.logger import setup_logger

# Set up logger for this module
logger = setup_logger("home", "home.log")

# Create a Blueprint for home
home_bp = Blueprint("home", __name__)

@home_bp.route('/')
def home_page():
    return render_template("index.html")

@home_bp.route('/old')
def home_old():
    return render_template("old.html")
