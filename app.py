import datetime
import sqlite3
import os
from urllib.parse import urlparse, urljoin
from operator import itemgetter
import re

from flask import Flask, flash, get_flashed_messages, render_template, redirect, request, url_for
from flask_bcrypt import Bcrypt
from flask_mde import Mde, MdeField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = os.urandom(16)
app.url_map.strict_slashes = False

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
app.config.update(
    REMEMBER_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_SECURE=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

pw_hash = bcrypt.generate_password_hash("testpass")
mde = Mde(app)

class User(UserMixin):

    def __init__(self, id, username, email, password, first_name, last_name):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.authenticated = False

    def is_active(self):
        return self.is_active()

    def is_anonymouse(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect('db/mt.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('select * from author where id = ?', [user_id])

        user = cur.fetchone()
        if user is None:
            return None

        id, username, email, password, first_name, last_name = itemgetter(
            'id', 'username', 'email', 'password', 'first_name', 'last_name')(dict(user))

        return User(id, username, email, password, first_name, last_name)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(),Length(min=4, max=15)])
    password = StringField('Password', validators=[InputRequired(),Length(min=8, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(),Length(min=4, max=15)])
    password = StringField('Password', validators=[InputRequired(),Length(min=8, max=80)])
    first_name = StringField('First Name', validators=[InputRequired(),Length(min=1, max=100)])
    last_name = StringField('Last Name', validators=[InputRequired(),Length(min=1, max=100)])

CREATE_POST = 'insert into post (author_id, pub_date, title, content, published) values (NULL, ?, ?, ?, ?, ?)'
UPDATE_POST = 'update post set pub_date = ?, title = ?, content = ?, published = ? where id = ?' 
TAGS_FOR_POST_BY_POST_ID = 'select tag.tag, tag.id from tag join post_tag on tag.id = post_tag.tag_id join post on post.id = post_tag.post_id where post_id = ?' 
CREATE_TAG = 'insert or ignore into tag values (NULL, ?)'
ADD_TAG_TO_POST = 'insert or ignore into post_tag values (NULL, ?, ?)'
DELETE_TAG_FROM_POST = 'delete from post_tag where post_tag.post_id = ? and post_tag.tag_id = ?'
ALL_POSTS_WITH_TAGS = '''
    select
      author.first_name, post.id, post.title, post.content, post.pub_date, post.published,
        group_concat(tag.tag, ",") as post_tags
        from post
        join post_tag on post.id = post_tag.post_id
        join tag on tag.id = post_tag.tag_id
        join post_author on post.id = post_author.post_id
        join author on post_author.author_id = author.id
        group by post.id;
    '''
POST_WITH_TAGS_BY_POST_ID = '''
select
  author.first_name as author_first_name,
  post.id, post.title, post.content, post.pub_date, post.published,
  group_concat(tag.tag, ",") as post_tags
    from post
    join post_tag on post.id = post_tag.post_id
    join tag on tag.id = post_tag.tag_id
    join post_author on post.id = post_author.post_id
    join author on post_author.author_id = author.id
    where post.id = ? 
'''

CREATE_AUTHOR = 'insert into author (username, email, first_name, last_name, password) values(?, ?, ?, ?, ?)';

def get_posts_with_tags():

    with sqlite3.connect('db/mt.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(ALL_POSTS_WITH_TAGS)
        posts = [ dict(row) for row in cur.fetchall() ]

        for post in posts:
            post['post_tags'] = [ tag for tag in post['post_tags'].split(',') if tag ]

        return posts

def get_post_with_tags(post_id): 

    with sqlite3.connect('db/mt.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(POST_WITH_TAGS_BY_POST_ID, [post_id])
        post = dict(cur.fetchone())
        post['post_tags'] = [ tag for tag in post['post_tags'].split(',') if tag ]

        return post

@app.route('/')
def index():
    return render_template('blog/index.html')

@app.route('/news')
def news():
    posts = get_posts_with_tags()
    return render_template('blog/news.html', posts=posts)

@app.route('/admin/dashboard')
@login_required
def dashboard():
    posts = get_posts_with_tags()
    return render_template('admin/dashboard.html', posts=posts)

@app.route('/admin')
def admin():
    return redirect('admin/dashboard')

@app.route('/admin/login', methods=['GET','POST'])
def login():

    form = LoginForm()
    error = None 

    if form.validate_on_submit():

        with sqlite3.connect('db/mt.db') as con:

            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("select * from author where username = ?", [form.username.data])
            result = cur.fetchone()

            if result is None:
                return render_template('admin/login.html', form=form, error='Invalid user/password combination')

            user = load_user(result['id'])

            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
            else:
                return render_template('admin/login.html', form=form, error='invalid user/password combination')

            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
            next = request.args.get('next')
            if not is_safe_url(next):
                return flask.abort(400)

            flash('You have been logged in successfully!', 'info')
            return redirect(url_for('dashboard'))

    else:
        return render_template('admin/login.html', form=form)

@login_required
@app.route('/admin/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        form = RegisterForm()
        return render_template('admin/login.html', form=form)
    elif request.method == 'POST':
        return render_template('admin/login.html')

@app.route('/admin/post/new', methods=['GET','POST'])
@login_required
def new_post():

    if request.method == 'GET':

        # design problem: another place to update when adding/ removing default values
        post = { 
            'content': 'abc', 
            'title': 'The ABC Are Really Cool' 
        }
        return render_template('admin/create-post.html', post=post)

    elif request.method == 'POST':

        pub_date = datetime.datetime.now()
        content = request.form.get('post-content')
        title = request.form.get('post-title')
        published = 0
        tags = [ tag for tag 
                 in re.split(r"[\s,]", request.form.get('post-tags', ''))
                 if len(tag) ]

        with sqlite3.connect('db/mt.db') as con:

            con.row_factory = sqlite3.Row
            cur = con.cursor()

            # create post
            cur.execute(CREATE_POST, (author, pub_date, title, content, published))
            post_id = cur.lastrowid

            # add tags to post, ensure no errors on duplicates with 'or ignore' clause
            # admits good data, prevents bad data w/out erros
            for tag in tags:

                cur.execute("insert or ignore into tag values (NULL, ?)", [tag])

                # tag is in db at this point, get its id
                cur.execute("select id from tag where tag = ?", [tag])
                new_tag = cur.fetchone()
                cur.execute("insert or ignore into post_tag values (NULL, ?, ?)", (post_id, new_tag['id']))

            con.commit()

            return redirect('/admin')

@app.route('/admin/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):

    if request.method == 'GET':

        post = get_post_with_tags(post_id)
        return render_template('admin/edit-post.html', post=post)

    if request.method == 'POST':

        author_id = 1 
        pub_date = datetime.datetime.now()
        content = request.form.get('post-content')
        title = request.form.get('post-title')
        published = 0
        tags = set([ tag.lower() for tag 
                 in re.split(r"[\s,]", request.form.get('post-tags', ''))
                 if len(tag) ])

        with sqlite3.connect('db/mt.db') as con:

            con.row_factory = sqlite3.Row
            cur = con.cursor()

            cur.execute(UPDATE_POST, (pub_date, title, content, published, post_id))

            cur.execute(TAGS_FOR_POST_BY_POST_ID, [post_id])
            old_tags_with_ids = dict(cur.fetchall()) # tag => id
            old_tags = set([tag.lower() for (tag, id) in old_tags_with_ids.items()])

            tags_to_delete = old_tags - tags 
            tags_to_add = tags - old_tags

            for tag in tags_to_delete:
                # TODO: if we remove a post_tag entry, and there are no posts w/ that tag, need to delete tag from tags table.
                # seems like a trigger is necessary?
                cur.execute(DELETE_TAG_FROM_POST, (post_id, old_tags_with_ids[tag]))

            for tag in tags_to_add:

                cur.execute(CREATE_TAG, [tag])

                # tag is in db at this point, get its id
                cur.execute("select id from tag where tag = ?", [tag])
                new_tag = cur.fetchone()
                cur.execute(ADD_TAG_TO_POST, (post_id, new_tag['id']))

            con.commit()

        return redirect('/admin')

@login_required
@app.route('/admin/post/<int:post_id>/publish', methods=['POST'])
def publish_post(post_id):
    
    with sqlite3.connect('db/mt.db') as con:
        cur = con.cursor()
        cur.execute('update posts set published = 1 where id = ?', [post_id])
        con.commit()

    return redirect('/admin')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
