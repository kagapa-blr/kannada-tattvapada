"""
Home route for displaying Tatvapada records in the main view.
"""

from flask import Blueprint, render_template

from app.utils.auth_decorator import login_required

# Create a Blueprint for home
home_bp = Blueprint("home", __name__)

@home_bp.route('/')
@login_required
def home_page():
    return render_template("index.html")

