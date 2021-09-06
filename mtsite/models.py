from mtsite.db import db

class User(db.Model):
    """Data model for user accounts."""

    __tablename__ = 'flasksqlalchemy-tutorial-users'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.String(64),
        unique=True,
        nullable=False
    )
    password = db.Column(
        db.String(80),
        index=True,
        nullable=False
    )
    first_name = db.Column(
        db.String(64)
    )
    last_name = db.Column(
        db.String(64)
    )
    is_active = db.Column(
        db.Boolean,
        nullable=False
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

def stub_post():
    return {
        'title': 'New Post',
        'content': '',
        'post_tags': []
    }
