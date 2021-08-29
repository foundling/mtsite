from flask import Blueprint, render_template

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
def dashboard():
    return 'dashboard'

@admin.route('/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    return 'get post ' + str(post_id)

@admin.route('/post/<int:post_id>', methods=['POST'])
def create_post(post_id):
    return 'create post ' + str(post_id)

@admin.route('/post/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    return 'update post ' + str(post_id)

