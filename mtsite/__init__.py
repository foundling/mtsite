# Purposes of this file:
# 1. contains the app factory (which prevents us from having to pass app object around
# 2. tells python that 'mtsite' should be a package
# https://flask.palletsprojects.com/en/2.0.x/tutorial/factory/

import os

from flask import Flask

def create_app(test_config=None, instance_relative_config=True):

    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'mt.db')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'hello, world!'

    from . import db
    db.init_app(app)
    
    from mtsite.blueprints.auth import auth
    app.register_blueprint(auth.bp, url_prefix='/auth')

    return app
