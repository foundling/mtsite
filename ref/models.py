from db import db

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), unique=True)
    password = db.Column(db.String(80))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    author_alias = db.Column(db.String(10), unique=True)
    is_active = db.Column(db.Boolean)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

'''
class PostTag(db.Model):
    # foreign key post_id refs post(id)
    # foreign key tag_id refs tag(id)
'''

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

'''
class PostCategory(db.Model):
    # foreign key post_id refs post(id)
    # foreign key category_id refs category(id)
'''
