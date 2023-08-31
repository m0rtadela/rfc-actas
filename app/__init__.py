from os import environ

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_principal import Principal, identity_loaded, UserNeed, RoleNeed, Permission

from .config import TestingConfig, ProductionConfig
from .sql_models import db, UserModel
# from .models import UserModel

#Blueprints
from .public import public as public_blueprint
from .auth import auth as auth_blueprint
from .sat import sat as sat_blueprint
from .robot import robot as robot_blueprint
from .cli import cli as cli_blueprint
from .admin import admin as admin_blueprint
from .robot.views import sat_robot

login_manager = LoginManager()
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(username):
    return UserModel.query_username(username)
    # return UserModel.query(username)


def create_app():
    app = Flask(__name__)
    
    app.config.from_object( ProductionConfig ) # config_options[environ.get('FLASK_CONFIG')]

    migrate = Migrate(app, db)
    principal = Principal(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        # Set the identity user object
        identity.user = current_user

        # Add the UserNeed to the identity
        if hasattr(current_user, 'username'):
            identity.provides.add(UserNeed(current_user.username))

        if hasattr(current_user, 'role'):
            print(current_user.role, "role")
            identity.provides.add(RoleNeed(current_user.role))
    
    # Initialize Flask Extensions
    Bootstrap(app)
    login_manager.init_app(app)
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(sat_blueprint, url_prefix='/sat')
    app.register_blueprint(robot_blueprint, url_prefix='/robot')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(public_blueprint, url_prefix='/')
    app.register_blueprint(cli_blueprint)
    
    with app.app_context():
        db.create_all()
    sat_robot.app = app

    @app.errorhandler(404)
    def page_not_found(e):
        context = {
            "error_code": 404,
            "error_message": "Pagina no encontrada"
        }
        return render_template('/errors/base_error.html.jinja', **context)

    @app.errorhandler(403)
    def not_access(e):
        context = {
            "error_code": 403,
            "error_message": "No tienes acceso a esta pagina"
        }
        return render_template('/errors/base_error.html.jinja', **context)
    
    @app.errorhandler(500)
    def not_access(e):
        context = {
            "error_code": 500,
            "error_message": "Error interno, intente mas tarde"
        }
        return render_template('/errors/base_error.html.jinja', **context)

    return app


