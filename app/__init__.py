import os
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate, mail, jwt, limiter, login_manager, csrf

# Path to the backend/public folder (one level above this package)
_PUBLIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")


def create_app(config_class=Config):
    app = Flask(__name__, static_folder=_PUBLIC_DIR, static_url_path="/static")
    app.config.from_object(config_class)

    cors_origins = app.config.get('CORS_ALLOWED_ORIGINS', [])

    app.logger.info(
        'Flask environment: %s',
        app.config.get('ENV_NAME', 'unknown'),
    )
    app.logger.info(
        'CORS_ORIGINS raw value: %s',
        app.config.get('CORS_ORIGINS_RAW'),
    )
    app.logger.info('CORS enabled origins: %s', cors_origins)
    if not cors_origins:
        app.logger.warning(
            'CORS enabled origins list is empty. '
            'Cross-origin browser requests will fail.'
        )

    # CORS – applied globally to the whole app.
    # Origin validation is the criterion; no path filtering.
    # This covers /api/*, /auth/*, /units, /areas, /admin/... and any
    # future endpoint without needing manual registration.
    CORS(
        app,
        origins=cors_origins,
        supports_credentials=app.config.get('CORS_SUPPORTS_CREDENTIALS', True),
        allow_headers=app.config.get('CORS_ALLOW_HEADERS', ()),
        methods=app.config.get('CORS_METHODS', ()),
    )

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    jwt.init_app(app)
    csrf.init_app(app)

    # Flask-Login (HTML admin panel session auth)
    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    login_manager.login_message = "Inicia sesión para acceder al panel."
    login_manager.login_message_category = "error"

    @login_manager.user_loader
    def load_user(user_id: str):
        from .models import User
        try:
            return User.query.get(int(user_id))
        except (TypeError, ValueError):
            return None

    try:
        limiter.init_app(app)
    except Exception as exc:
        app.logger.warning(f"Rate limiter error: {exc}")

    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return jsonify({"error": "Token requerido.", "reason": reason}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "Token inválido.", "reason": reason}), 422

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token expirado. Por favor inicia sesión de nuevo."}), 401

    # Blueprints
    from .health import health_bp
    app.register_blueprint(health_bp)

    from .api import api_bp
    app.register_blueprint(api_bp)

    from .api import auth_public_bp
    app.register_blueprint(auth_public_bp)

    # Exempt the REST API from CSRF (it uses JWT Bearer tokens)
    csrf.exempt(api_bp)
    csrf.exempt(auth_public_bp)

    # Admin HTML panel
    from .admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # CLI
    from .commands import (
        create_admin,
        init_db,
        seed_demo,
        sync_schema,
        repair_alembic,
    )
    app.cli.add_command(create_admin)
    app.cli.add_command(init_db)
    app.cli.add_command(seed_demo)
    app.cli.add_command(sync_schema)
    app.cli.add_command(repair_alembic)

    # Import models so Flask-Migrate can detect them
    from . import models  # noqa: F401

    # -----------------------------------------------------------------------
    # Favicon routes for browser requests
    # -----------------------------------------------------------------------
    @app.route("/favicon.svg")
    def favicon_svg():
        return send_from_directory(_PUBLIC_DIR, "favicon.svg", mimetype="image/svg+xml")

    @app.route("/favicon.ico")
    def favicon_ico():
        if os.path.exists(os.path.join(_PUBLIC_DIR, "favicon.ico")):
            return send_from_directory(_PUBLIC_DIR, "favicon.ico", mimetype="image/x-icon")
        return send_from_directory(_PUBLIC_DIR, "favicon.svg", mimetype="image/svg+xml")

    @app.route("/")
    def index():
        return render_template("errors/not_found.html"), 404

    def _is_api_request() -> bool:
        return (
            request.path.startswith('/api/')
            or request.path.startswith('/auth/')
        )

    @app.errorhandler(404)
    def not_found(_error):
        if _is_api_request():
            return jsonify({"error": "No encontrado."}), 404
        return render_template("errors/not_found.html"), 404

    @app.errorhandler(403)
    def forbidden(_error):
        if _is_api_request():
            return jsonify({"error": "Acceso denegado."}), 403
        return render_template("errors/not_found.html"), 404

    return app
