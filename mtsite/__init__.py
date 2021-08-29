from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'SECRETKEY'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/mt.db'

    db.init_app(app)

    @app.route('/')
    def index():
        render_template('index.html')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/admin')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint,  url_prefix='/admin')

    return app
