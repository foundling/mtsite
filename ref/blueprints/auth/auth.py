from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/register')
def register():
    return 'render a registration form here.  username, password, password confirmation, first name, last name.'

@auth.route('/login')
def login():
    return 'render login form here.  username, password, token.'

@auth.route('/logout')
def logout():
    return 'logs a user out'

