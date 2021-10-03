from flask import Blueprint, render_template

bp = Blueprint('blog', __name__, template_folder='templates', static_folder='static')

from mtsite.blueprints.blog.posts import posts 

@bp.route('/')
def index():
    return render_template('blog/index.html', posts=posts)
