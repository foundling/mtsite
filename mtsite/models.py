from FlaskLogin import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    # username
    # password
    # firstname
    # lastname
    # author alias (default is first name, last name)
    # active
    pass

class Post(db.Model):
    # title
    # content
    pass

class Tag(db.Model):
    # name
    pass

class PostTag(db.Model):
    # foreign key post_id refs post(id)
    # foreign key tag_id refs tag(id)
    pass

class Category(db.Model):
    # name
    pass

class PostCategory(db.Model):
    # foreign key post_id refs post(id)
    # foreign key category_id refs category(id)
    pass
