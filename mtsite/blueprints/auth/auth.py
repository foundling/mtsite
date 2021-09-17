from io import BytesIO

from flask import abort, Blueprint, flash, redirect, render_template, url_for, session
from flask_login import current_user, login_user, logout_user
import pyqrcode

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

        session['username'] = user.username
        return redirect(url_for('auth.two_factor_setup'))

    else:
        flash('Invalid Form Input')
        print(form.errors)

    return redirect(url_for('auth.register'))

@bp.route('qrcode')
def qrcode():

    if 'username' not in session:
        abort(404)
 
    user = User.query.filter_by(username=session['username']).first()

    if user is None:
        abort(404)

    del session['username']

    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=5)

    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, mustrevalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }


@bp.route('/twofactor')
def two_factor_setup():

    if 'username' not in session:
        return redirect(url_for('auth.register')) # FIXME: is this right?

    user = User.query.filter_by(username=session['username']).first()
    if user is None:
        return redirect(url_for('auth.register'))

    return render_template('auth/two_factor_setup.html'), 200, {
        'Cache-control': 'no-cache, no-store, must-revalidate',
        'pragma': 'no-cache',
        'Expires': '0'
    }

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

        if user is None or not user.check_password(form.password.data) or \
                not user.verify_totp(form.token.data):
            flash('Invalid username, password or token.')
            return redirect(url_for('auth.login'))

        login_user(user)
        return redirect(url_for('admin.dashboard'))

    return render_template('login')

@bp.route('/logout', methods=['GET'])
def logout():

    if current_user.is_authenticated:
        logout_user()

    return redirect(url_for('auth.login'))

