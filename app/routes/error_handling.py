from flask import Blueprint, render_template

# Blueprint for error handling
errors_bp = Blueprint("errors", __name__, url_prefix="/errors")

# 404 Not Found
@errors_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template("errors/NotFound-404.html", code=404, message="Page Not Found"), 404

# 405 Method Not Allowed
@errors_bp.app_errorhandler(405)
def method_not_allowed(e):
    return render_template("errors/MethodNotFound-405.html", code=405, message="Method Not Allowed"), 405

# Optional: generic error fallback
@errors_bp.app_errorhandler(Exception)
def handle_exception(e):
    return render_template("errors/error.html", code=500, message="Internal Server Error"), 500
