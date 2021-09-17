from flask import Blueprint, flash, redirect, render_template, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired
from flask_login import current_user, login_user, logout_user

from mtsite.models import User
from mtsite.forms import RegistrationForm, LoginForm
from mtsite import db

bp = Blueprint('auth', __name__, template_folder='templates')


@bp.route('/register', methods=['GET'])
def register_form():
    form = RegistrationForm()
    return render_template('auth/register.html', form=form)

@bp.route('/register', methods=['POST'])
def register():

    form = RegistrationForm()

    if form.validate_on_submit():

        user = User(username=form.username.data, first_name=form.first_name.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Registration Successful!')
        return redirect(url_for('auth.login'))

    else:
        flash('Invalid Form Input')

    return redirect(url_for('auth.register'))

@bp.route('/login', methods=['GET'])
def login():
    form = LoginForm()
    return render_template('auth/login.html', form=form)

@bp.route('/login', methods=['POST'])
def validate_login():

    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        login_user(user)
        return redirect(url_for('admin.dashboard'))

    return render_template('login')

@bp.route('/logout', methods=['GET'])
def logout():

    if current_user.is_authenticated:
        logout_user()

    return redirect(url_for('auth.login'))

