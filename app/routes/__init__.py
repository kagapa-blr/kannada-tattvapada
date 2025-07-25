def register_routes(app):
    from .home import home_bp
    app.register_blueprint(home_bp)
