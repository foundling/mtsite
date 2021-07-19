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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news')
def news():
    with sqlite3.connect('db/mt.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        posts = cur.execute('select * from post order by pub_date desc')
        return render_template('news.html', posts=posts)

@app.route('/admin')
def all_posts():
    with sqlite3.connect('db/mt.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        posts = cur.execute('select * from post order by pub_date desc')
        return render_template('admin.html', posts=posts)

@app.route('/admin/post/new')
def new_post():
    return render_template('admin-new.html', article_text="# New Article")

@app.route('/admin/post/create', methods=['GET'])
def x():

    with sqlite3.connect('db/mt.db') as con:

        con.row_factory = sqlite3.Row
        cur.execute('select * from post order by pub_date desc')
        posts = cur.fetchall()

        return render_template('admin.html', posts=posts)

@app.route('/admin/post/create', methods=['POST'])
def new_blog_post():

    author = 'alex'
    pub_date = datetime.datetime.now()
    content = request.form.get('post-content')
    title = request.form.get('post-title')
    tags = [ tag for tag in re.split(r"[\s,]", request.form.get('post-tags', '')) if len(tag) ]

    with sqlite3.connect('db/mt.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('insert into post values (NULL, ?, ?, ?, ?)', (author, pub_date, title, content))
        post_id = cur.lastrowid

        for tag in tags:
            cur.execute('insert into tag values (NULL, ?)', (tag))
            tag_id = cur.lastrowid
            cur.execute('insert into post_tag values (NULL, ?, ?)', (post_id, tag_id))
        con.commit()

        return redirect('/admin')

@app.route('/admin/post/<int:post_id>/edit')
def edit_post(post_id):

    with sqlite3.connect('db/mt.db') as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('select * from post where id = ?', (post_id))
        post = cur.fetchone()
        return render_template('admin-new.html', article_text="# New Article", post=post)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
