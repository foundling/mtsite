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

CREATE_POST = 'insert into post values (NULL, ?, ?, ?, ?, ?)'
UPDATE_POST = 'update post set author = ?, pub_date = ?, title = ?, content = ?, published = ? where id = ?' 
TAGS_FOR_POST_BY_POST_ID = 'select tag.tag, tag.id from tag join post_tag on tag.id = post_tag.tag_id join post on post.id = post_tag.post_id where post_id = ?' 
CREATE_TAG = 'insert or ignore into tag values (NULL, ?)'
ADD_TAG_TO_POST = 'insert or ignore into post_tag values (NULL, ?, ?)'
DELETE_TAG_FROM_POST = 'delete from post_tag where post_tag.post_id = ? and post_tag.tag_id = ?'
ALL_POSTS_WITH_TAGS = '''
    select
      post.id, post.author, post.title, post.content, post.pub_date, post.published,
        group_concat(tag.tag, ",") as post_tags
        from post
        join post_tag on post.id = post_tag.post_id
        join tag on tag.id = post_tag.tag_id
        group by post.id;
    '''
POST_WITH_TAGS_BY_POST_ID = '''
select
  post.id, post.author, post.title, post.content, post.pub_date, post.published,
  group_concat(tag.tag, ",") as post_tags
    from post
    join post_tag on post.id = post_tag.post_id
    join tag on tag.id = post_tag.tag_id
    where post.id = ? 
'''


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
        cur.execute(POST_WITH_TAGS_BY_POST_ID, (post_id,))
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

@app.route('/admin')
def all_posts():

    posts = posts = get_posts_with_tags()
    return render_template('admin/index.html', posts=posts)

@app.route('/admin/post/new', methods=['GET','POST'])
def new_post():

    if request.method == 'GET':

        # design problem: another place to update when adding/ removing default values
        post = { 
            'content': 'abc', 
            'title': 'The ABC Are Really Cool' 
        }
        return render_template('admin/create-post.html', post=post)

    elif request.method == 'POST':

        author = 'alex'
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

                cur.execute("insert or ignore into tag values (NULL, ?)", (tag,))

                # tag is in db at this point, get its id
                cur.execute("select id from tag where tag = ?", (tag,))
                new_tag = cur.fetchone()
                cur.execute("insert or ignore into post_tag values (NULL, ?, ?)", (post_id, new_tag['id']))

            con.commit()

            return redirect('/admin')

@app.route('/admin/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):

    if request.method == 'GET':

        post = get_post_with_tags(post_id)
        return render_template('admin/edit-post.html', post=post)

    if request.method == 'POST':

        author = 'alex'
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

            cur.execute(UPDATE_POST, (author, pub_date, title, content, published, post_id))

            cur.execute(TAGS_FOR_POST_BY_POST_ID, (post_id,))
            old_tags_with_ids = dict(cur.fetchall()) # tag => id
            old_tags = set([tag.lower() for (tag, id) in old_tags_with_ids.items()])

            tags_to_delete = old_tags - tags 
            tags_to_add = tags - old_tags

            for tag in tags_to_delete:
                # TODO: if we remove a post_tag entry, and there are no posts w/ that tag, need to delete tag from tags table.
                # seems like a trigger is necessary?
                cur.execute(DELETE_TAG_FROM_POST, (post_id, old_tags_with_ids[tag]))

            for tag in tags_to_add:

                cur.execute(CREATE_TAG, (tag,))

                # tag is in db at this point, get its id
                cur.execute("select id from tag where tag = ?", (tag,))
                new_tag = cur.fetchone()
                cur.execute(ADD_TAG_TO_POST, (post_id, new_tag['id']))

            con.commit()

        return redirect('/admin')

@app.route('/admin/post/<int:post_id>/publish', methods=['POST'])
def publish_post(post_id):
    
    with sqlite3.connect('db/mt.db') as con:
        cur = con.cursor()
        cur.execute('update posts set published = 1 where id = ?', (post_id,))
        con.commit()

    return redirect('/admin')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
