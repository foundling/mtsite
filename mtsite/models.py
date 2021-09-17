import os
import base64
import onetimepass

from mtsite import db
from mtsite import login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime
from mtsite import db

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):

    otp_secret = db.Column(db.String(16))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.otp_secret is None:
            self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password): 
        return check_password_hash(self.password_hash, password)

    def get_totp_uri(self):
        return 'otpauth://totp/mtsite:{0}?secret={1}&issuer=mtsite'.format(self.username, self.otp_secret)

    def verify_totp(self, token):
        return onetimepass.valid_totp(token, self.otp_secret)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
