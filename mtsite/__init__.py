from flask import Flask
from mtsite.db import db

def create_app(env):

    app = Flask(__name__)
    db.init_app(app)
    app.config['SECRET_KEY'] = 'SECRETKEY'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/mt.db'

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint,  url_prefix='/')

    from .blog import blog as blog_blueprint
    app.register_blueprint(blog_blueprint,  url_prefix='/blog')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/admin')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint,  url_prefix='/admin')

    with app.app_context():
        db.create_all()

    return app
