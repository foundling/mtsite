from flask import Blueprint, render_template

bp = Blueprint('blog', __name__, template_folder='templates', static_folder='static')

from mtsite.blueprints.blog.posts import posts 

@bp.route('/')
def blog():
    return render_template('blog/index.html', posts=posts)

@bp.route('/post/<int:post_id>')
def post(post_id):
    return render_template('blog/post.html', post=posts[post_id])
