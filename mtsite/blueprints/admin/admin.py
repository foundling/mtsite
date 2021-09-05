from flask import Blueprint, request, flash
from flask.templating import render_template

from mtsite.db import get_db
from mtsite.models import stub_post

bp = Blueprint('admin', __name__, template_folder='templates')

@bp.route('/dashboard')
def index():
    return render_template('admin/dashboard.html')

# Forms for post CRUD
@bp.route('/post/form/create')
def post_create_form():
    
    post = stub_post
    return render_template('admin/forms/create-post.html', post=post)

@bp.route('/post/form/update')
def post_update_form():

    db = get_db()
    post = {}

    return render_template('admin/forms/update-post.html', post=post)

# endpoints for db changes
@bp.route('/post', methods=['POST'])
def create_post():

    title = request.form.get('title')
    tags = request.form.get('tags')
    content = request.form.get('content')

    db = get_db()

    flash('post created!')
    return render_template('admin/dashboard.html')

@bp.route('/post', methods=['PUT'])
def update_post():

    title = request.form.get('title')
    tags = request.form.get('tags')
    content = request.form.get('content')

    db = get_db()

    flash('post updated!')
    return render_template('admin/dashboard.html')
