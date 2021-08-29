from flask import Blueprint, render_template

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
def dashboard():
    return 'dashboard'

# blank form for creating new post
@admin.route('/post/createform', methods=['GET'])
def create_form(post_id):
    return 'blank form for creating new post'

# fetch a post for editing
@admin.route('/post/<int:post_id>/editform', methods=['GET'])
def get_post(post_id):
    return 'form with post data populated'

# create new post endpoint. post to here from a form where new post was created
@admin.route('/post/new', methods=['POST'])
def create_post():
    return 'create post ' + str(post_id)

# update post endpoint. put to here from a form where you've edited an existing post
@admin.route('/post/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    return 'update post ' + str(post_id)

@admin.route('/profile', methods=['GET'])
def get_profile():
    return 'render profile details here'

@admin.route('/profile', methods=['PUT'])
def update_profile():
    return 'render editable profile details here'



