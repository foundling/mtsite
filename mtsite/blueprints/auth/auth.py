from flask import Blueprint, flash, redirect, render_template, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired

from mtsite.models import User
from mtsite import db

bp = Blueprint('auth', __name__, template_folder='templates')


class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], default='aramsdell')
    first_name = StringField('First Name', validators=[DataRequired()], default='alex')
    last_name = StringField('Last Name', validators=[DataRequired()], default='ramsdell')
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()], default='testpass')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], default='aramsdell')
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


@bp.route('/register', methods=['GET'])
def register_form():
    form = SignupForm()
    return render_template('auth/register.html', form=form)

@bp.route('/register', methods=['POST'])
def register():

    form = SignupForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        first_name = form.first_name.data
        last_name = form.last_name.data
        hashed_pw = generate_password_hash(password, 'sha256')
        user = User(
            username=username,
            password=hashed_pw,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )

        db.session.add(user)
        db.session.commit()

        flash('You have been successfully registered!')
        return redirect(url_for('auth.login'))

    else:
        flash('Invalid Form Input')

    return redirect(url_for('auth.register'))

'''
@bp.route('/login', methods=['GET'])
def login():
    form = LoginForm()
    return render_template('auth/login.html', form=form)

@bp.route('/login', methods=['POST'])
def validate_login():

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.username.data

        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('auth.validate_login'))

'''
