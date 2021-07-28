import datetime
import sqlite3
import re

from flask import Flask, render_template, redirect, request
from flask_mde import Mde, MdeField
from flask_wtf import FlaskForm

app = Flask(__name__)
app.url_map.strict_slashes = False
mde = Mde(app)
app.config['SECRET_KEY'] = 'SECRET'


def get_posts_with_tags():

    posts_with_tags_query = '''
    select
      post.id, post.author, post.title, post.content, post.pub_date, post.published,
        group_concat(tag.tag, ",") as post_tags
        from post
        join post_tag on post.id = post_tag.post_id
        join tag on tag.id = post_tag.tag_id
        group by post.id;
    '''

    with sqlite3.connect('db/mt.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        posts = list(cur.execute(posts_with_tags_query))

        for post in posts:
            post.post_tags = filter(lambda: bool(x), post.post_tags.split(','))

        return posts

def get_post_with_tags(post_id): 

    post_with_tags_query = '''
    select
      post.id, post.author, post.title, post.content, post.pub_date, post.published,
      group_concat(tag.tag, ",") as post_tags
        from post
        join post_tag on post.id = post_tag.post_id
        join tag on tag.id = post_tag.tag_id
        where post.id = ? 
    '''

    with sqlite3.connect('db/mt.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(post_with_tags_query, (post_id,))
        post = cur.fetchone()
        post.post_tags = filter(lambda: bool(x), post.post_tags.split(','))

        return post


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news')
def news():

    posts = get_posts_with_tags()
    return render_template('news.html', posts=posts)

@app.route('/admin')
def all_posts():

    return render_template('admin/index.html', posts = get_posts_with_tags())

@app.route('/admin/post/new')
def new_post():
    # design problem: another place to update when adding/ removing default values
    post = { 'content': '# New Post' }
    return render_template('admin/create-or-edit-post.html', post=post, mode="new")

@app.route('/admin/post/create', methods=['POST'])
def create_post():

    author = 'alex'
    pub_date = datetime.datetime.now()
    content = request.form.get('post-content')
    title = request.form.get('post-title')
    published = 0
    tags = [ tag 
             for tag in re.split(r"[\s,]", request.form.get('post-tags', ''))
             if len(tag) ]

    with sqlite3.connect('db/mt.db') as con:

        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('insert into post values (NULL, ?, ?, ?, ?, ?)', (author, pub_date, title, content, published))
        post_id = cur.lastrowid

        for tag in tags:
            cur.execute('insert into tag values (NULL, ?)', (tag))
            tag_id = cur.lastrowid
            cur.execute('insert into post_tag values (NULL, ?, ?)', (post_id, tag_id))

        con.commit()

        return redirect('/admin')

@app.route('/admin/post/<int:post_id>/publish', methods=['POST'])
def publish_post(post_id):
    
    with sqlite3.connect('db/mt.db') as con:
        cur = con.cursor()
        cur.execute('update posts set published = 1 where id = ?', (post_id,))
        con.commit()

    return redirect('/admin')

@app.route('/admin/post/<int:post_id>/edit', methods=['POST'])
def edit_post(post_id):

    post = get_post_with_tags(post_id)
    return render_template('admin/create-or-edit-post.html', post=post, mode="edit")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
