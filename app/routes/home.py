"""
Home route for displaying Tatvapada records in the main view.
"""

from flask import Blueprint, render_template, request, session, redirect, url_for

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

@home_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Replace this with your actual validation logic
        if username == "admin" and password == "password":
            session['user'] = username  # or user ID
            return redirect(url_for('home.home_page'))  # or any secured page
        else:
            error = "ತಪ್ಪಾದ ಬಳಕೆದಾರ ಹೆಸರು ಅಥವಾ ಗುಪ್ತಪದ"
            return render_template("login.html", error=error)

    return render_template("login.html")

