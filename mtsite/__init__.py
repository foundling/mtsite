# Purposes of this file:
# 1. contains the app factory (which prevents us from having to pass app object around
# 2. tells python that 'mtsite' should be a package
# https://flask.palletsprojects.com/en/2.0.x/tutorial/factory/

from flask import Flask
from flask_mde import Mde
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from slugify import slugify

from config import Config

db = SQLAlchemy()
mde = Mde()
login = LoginManager()

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    mde.init_app(app)
    db.init_app(app)
    Migrate(app, db)
    login.init_app(app)

    from mtsite.blueprints.main import main
    app.register_blueprint(main.bp, url_prefix='/')

    from mtsite.blueprints.auth import auth
    app.register_blueprint(auth.bp, url_prefix='/auth')

    from mtsite.blueprints.admin import admin
    app.register_blueprint(admin.bp, url_prefix='/admin')

    from mtsite.blueprints.blog import blog
    app.register_blueprint(blog.bp, url_prefix='/blog')

    @app.template_filter('slug')
    def slug(s):
        return slugify(s)

    return app

from mtsite import models
