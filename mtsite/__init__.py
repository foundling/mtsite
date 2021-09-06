# Purposes of this file:
# 1. contains the app factory (which prevents us from having to pass app object around
# 2. tells python that 'mtsite' should be a package
# https://flask.palletsprojects.com/en/2.0.x/tutorial/factory/

import os

from flask import Flask, g
from flask_mde import Mde


def create_app(test_config=None, instance_relative_config=True):

    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(app.instance_path, 'mt.db')),
        SQLALCHEMY_TRACK_MODIFICATIONS  = False,
        SECRET_KEY = 'dev'
    )

    Mde(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register db commands
    with app.app_context():
        from mtsite import db
 
        db.init_app(app)
        g.db = db

        # apply blueprints
        from mtsite.blueprints.main import main
        app.register_blueprint(main.bp, url_prefix='/')

        from mtsite.blueprints.auth import auth
        app.register_blueprint(auth.bp, url_prefix='/auth')

        from mtsite.blueprints.admin import admin
        app.register_blueprint(admin.bp, url_prefix='/admin')


    return app
