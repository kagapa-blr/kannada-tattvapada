"""
Home route for displaying Tatvapada records in the main view.
"""

from flask import Blueprint, render_template, request, session, redirect, url_for

from app.utils.auth_decorator import login_required
from app.utils.logger import setup_logger


# Create a Blueprint for home
home_bp = Blueprint("home", __name__)

@home_bp.route('/')
def home_page():
    return render_template("index.html")

