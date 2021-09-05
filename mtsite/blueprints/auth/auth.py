import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from mtsite.db import get_db

bp = Blueprint('auth', __name__)

@bp.route('/login')
def login():

    db = get_db()
    result = db.execute('select * from user').fetchone()
    print(result)
    return str(result) 
