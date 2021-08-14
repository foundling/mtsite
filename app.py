import datetime
import sqlite3
import base64
import os
from urllib.parse import urlparse, urljoin
from operator import itemgetter
import onetimepass
import re

import pyqrcode
from io import BytesIO


from flask import Flask, flash, get_flashed_messages, render_template, redirect, request, url_for
from flask_bcrypt import Bcrypt
from flask_mde import Mde, MdeField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo
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

mde = Mde(app)

class User(UserMixin):

    def __init__(self, id, username, password, first_name, last_name, otp_secret):

        self.otp_secret = otp_secret # gets set when user initiates this flow
        self.id = id
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.authenticated = False

    def get_totp_uri(self):
        return 'otpauth://totp/MT-2FA:{0}?secret={1}&issuer=MT-2FA'.format(self.username, self.otp_secret)

    def verify_totp(self, token):
        return onetimepass.valid_totp(token, self.otp_secret)

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        # TODO: impliment this 
        return self.active

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect('db/mt.db', detect_types=sqlite3.PARSE_DECLTYPES) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('select * from user join author on user.id = author.author_id where author_id = ?', [user_id])

        user = cur.fetchone()
        if user is None:
            return None

        id, username, password, first_name, last_name, otp_secret = itemgetter(
            'id', 'username', 'password', 'first_name', 'last_name', 'otp_secret')(dict(user))

        return User(id, username, password, first_name, last_name, otp_secret)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    remember = BooleanField('Remember me')

class AuthForm(FlaskForm):
    auth_code = StringField('Code', validators=[InputRequired(),Length(min=6, max=6)])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(),Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(),Length(min=8), EqualTo('confirm_password', message='passwords must match') ])
    confirm_password = PasswordField('Confirm Password', validators = [InputRequired(), Length(min=8)])
    first_name = StringField('First Name', validators=[InputRequired(),Length(min=1, max=100)])
    last_name = StringField('Last Name', validators=[InputRequired(),Length(min=1, max=100)])

CREATE_POST = 'insert into post (author_id, pub_date, title, content, published) values (?, ?, ?, ?, ?)'
UPDATE_POST = 'update post set pub_date = ?, title = ?, content = ?, published = ? where id = ?' 
TAGS_FOR_POST_BY_POST_ID = 'select tag.tag, tag.id from tag join post_tag on tag.id = post_tag.tag_id join post on post.id = post_tag.post_id where post_id = ?' 
CREATE_TAG = 'insert or ignore into tag (tag) values (?)'
ADD_TAG_TO_POST = 'insert or ignore into post_tag (post_id, tag_id) values (?, ?)'
DELETE_TAG_FROM_POST = 'delete from post_tag where post_tag.post_id = ? and post_tag.tag_id = ?'
ALL_POSTS_WITH_TAGS = '''
select
    author.first_name, author.author_id, post.id, post.title, post.content, post.pub_date, post.published, group_concat(tag.tag, ",") as post_tags
    from post
    join author on post.author_id = author.author_id
    LEFT join post_tag on post.id = post_tag.post_id
    LEFT join tag on post_tag.tag_id = tag.id
    group by post.id;
'''
POST_WITH_TAGS_BY_POST_ID = '''
select

    author.first_name, author.author_id,
    post.id, post.title, post.content, post.pub_date, post.published, group_concat(tag.tag, ",") as post_tags

    from post
    join author on post.author_id = author.author_id
    LEFT join post_tag on post.id = post_tag.post_id
    LEFT join tag on post_tag.tag_id = tag.id
    where post.id = ?;
'''

def get_posts_with_tags():

    with sqlite3.connect('db/mt.db', detect_types=sqlite3.PARSE_DECLTYPES) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(ALL_POSTS_WITH_TAGS)
        posts = [ dict(row) for row in cur.fetchall() ]

        for post in posts:
            if post['post_tags'] is None:
                post['post_tags'] = []
            else:
                post['post_tags'] = [ tag for tag in post['post_tags'].split(',') if tag ]

        return posts

def get_post_with_tags(post_id): 

    with sqlite3.connect('db/mt.db', detect_types=sqlite3.PARSE_DECLTYPES) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(POST_WITH_TAGS_BY_POST_ID, [post_id])
        post = dict(cur.fetchone())

        if post['post_tags'] is None:
            post['post_tags'] = []
        else:
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
    posts_for_logged_in_author = [
        post for post
        in get_posts_with_tags()
        if post['author_id'] == current_user.get_id()
    ]
    return render_template('admin/dashboard.html', posts=posts_for_logged_in_author)

@app.route('/admin')
def admin():
    return redirect(url_for('dashboard'))

@app.route('/admin/activate')
def activate():
    return 'activate'

@app.route('/admin/two_factor_setup', methods=['GET'])
def two_factor_setup():

    return render_template('admin/two_factor_setup.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}

@app.route('/admin/two_factor_auth', methods=['GET', 'POST'])
def two_factor_auth():

    form = AuthForm()

    if form.validate_on_submit():

        if not user.verify_totp(form.auth_code.data):
            flash('Invalid username, password or token.')
            return redirect(url_for('two_factor_auth'))

        with sqlite3.connect('db/mt.db', detect_types=sqlite3.PARSE_DECLTYPES) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute('update user set otp_secret = ?, active = 1 where id = ?', [otp_secret, current_user.get_id()]) 
            return redirect(url_for('dashboard'))

    return render_template('admin/two_factor_auth.html', form=form)

@app.route('/admin/qrcode')
def qrcode():

    #TODO: restore security checks of username against session
    # e.g., https://github.com/miguelgrinberg/two-factor-auth-flask/blob/master/app.py#L128

    # render qrcode for FreeTOTP
    url = pyqrcode.create(current_user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}

@app.route('/admin/login', methods=['GET','POST'])
def login():

    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if form.validate_on_submit():

        with sqlite3.connect('db/mt.db', detect_types=sqlite3.PARSE_DECLTYPES) as con:

            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("select * from author join user on author.author_id = user.id where username = ?", [form.username.data])
            result = cur.fetchone()

            if result is None:
                flash('Invalid user/password combination', 'error')
                return render_template('admin/login.html', form=form)

            user = load_user(result['id'])

            if bcrypt.check_password_hash(user.password, form.password.data):

                login_user(user, remember=form.remember.data)
                user.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

                if user.otp_secret and user.active:
                    # user has enabled two factor auth, and needs to enter code
                    return redirect(url_for('two_factor_auth'))
                else:
                    # user hasn't enabled two factor auth
                    return redirect(url_for('two_factor_setup')) 


            else:
                flash('Invalid user/password combination', 'error')
                return render_template('admin/login.html', form=form)

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

    form = RegisterForm()

    if form.validate_on_submit(): 
        # check no user in db exists
        with sqlite3.connect('db/mt.db', detect_types=sqlite3.PARSE_DECLTYPES) as con:

            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute('select * from user where username = ?', [form.username.data])
            result = cur.fetchone()

            if result is not None:
                flash('Username is taken')
                return render_template('admin/register.html', form=form)

            # create user and author records for new user
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            cur.execute('insert into user username = ?, password = ?', [form.username.data, hashed_password])
            new_user_id = cur.lastrowid
            cur.execute('insert into author author_id = ?, first_name = ?, last_name = ?', [new_user_id, form.first_name.data, form.last_name.data])

            con.commit()

        return redirect(url_for('login'))

    return render_template('admin/register.html', form=form)

@app.route('/admin/post/new', methods=['GET','POST'])
@login_required
def new_post():


    if request.method == 'GET':

        # design problem: another place to update when adding/ removing default values
        post = { 'content': '', 'title': '' }

        return render_template('admin/create-post.html', post=post)

    elif request.method == 'POST':

        pub_date = datetime.datetime.now().strftime('%Y-%m-%d')
        content = request.form.get('post-content')
        title = request.form.get('post-title')
        published = 0
        tags = [ tag for tag 
                 in re.split(r"[\s,]", request.form.get('post-tags', ''))
                 if len(tag) ]

        with sqlite3.connect('db/mt.db', detect_types=sqlite3.PARSE_DECLTYPES) as con:

            con.row_factory = sqlite3.Row
            cur = con.cursor()

            author_id = current_user.id
            cur.execute(CREATE_POST, [author_id, pub_date, title, content, published])
            post_id = cur.lastrowid
            con.commit()

            # add tags to post, ensure no errors on duplicates with 'or ignore' clause
            # admits good data, prevents bad data w/out erros
            for tag in tags:

                cur.execute(CREATE_TAG, [tag])

                # tag is in db at this point, get its id
                cur.execute("select id from tag where tag = ?", [tag])
                new_tag = cur.fetchone()
                cur.execute(ADD_TAG_TO_POST, [post_id, new_tag['id']])

            con.commit()

            cur.execute(ALL_POSTS_WITH_TAGS)
            posts = [post for post in cur.fetchall()]

            return redirect(url_for('dashboard'))

@app.route('/admin/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):

    if request.method == 'GET':

        post = get_post_with_tags(post_id)
        return render_template('admin/edit-post.html', post=post)

    if request.method == 'POST':

        author_id = current_user.get_id()
        pub_date = datetime.datetime.now().strftime('%Y-%m-%d')
        content = request.form.get('post-content')
        title = request.form.get('post-title')
        published = 0
        tags = set([ tag.lower() for tag 
                 in re.split(r"[\s,]", request.form.get('post-tags', ''))
                 if len(tag) ])

        with sqlite3.connect('db/mt.db', detect_types=sqlite3.PARSE_DECLTYPES) as con:

            con.row_factory = sqlite3.Row
            cur = con.cursor()

            cur.execute(UPDATE_POST, (pub_date, title, content, published, post_id))

            cur.execute(TAGS_FOR_POST_BY_POST_ID, [post_id])
            con.commit()

            old_tags_with_ids = dict(cur.fetchall()) # tag => id
            old_tags = set([tag.lower() for (tag, id) in old_tags_with_ids.items()])

            tags_to_delete = old_tags - tags 
            tags_to_add = tags - old_tags

            for tag in tags_to_delete:
                # TODO: if we remove a post_tag entry, and there are no posts w/ that tag, need to delete tag from tags table.
                # seems like a trigger is necessary?
                cur.execute(DELETE_TAG_FROM_POST, (post_id, old_tags_with_ids[tag]))

            con.commit()

            for tag in tags_to_add:

                cur.execute(CREATE_TAG, [tag])

                # tag is in db at this point, get its id
                cur.execute("select id from tag where tag = ?", [tag])
                new_tag = cur.fetchone()
                cur.execute(ADD_TAG_TO_POST, (post_id, new_tag['id']))

            con.commit()

        return redirect(url_for('admin'))

@login_required
@app.route('/admin/post/<int:post_id>/publish', methods=['POST'])
def publish_post(post_id):
    
    with sqlite3.connect('db/mt.db', detect_types=sqlite3.PARSE_DECLTYPES) as con:
        cur = con.cursor()
        cur.execute('update post set published = 1 where id = ?', [post_id])
        con.commit()

    return redirect(url_for('admin'))

@app.errorhandler(404)
def page_not_found(error):

    return render_template('page_not_found.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
