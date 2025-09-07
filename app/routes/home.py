"""
Home route for displaying Tatvapada records in the main view.
"""
import time

from flask import Blueprint
from flask import render_template

from app.utils.auth_decorator import login_required

# Create a Blueprint for home
home_bp = Blueprint("home", __name__)

@home_bp.route('/')
@login_required
def home_page():
    return render_template("index.html")
