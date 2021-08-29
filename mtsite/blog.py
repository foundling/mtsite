from flask import Blueprint

blog = Blueprint('blog', __name__)

@blog.route('/post/<int:post_index>', methods=['GET'])
def get_one_post(post_index):
    # render a single blog post
    return 'render a specific blog post here'

@blog.route('/posts', methods=['GET'])
def get_all_posts():
    # render all posts or paged version
    return 'return all blog posts, preferably paged.'

@blog.route('/search')
def search_blog():
    search_query = request.args.get('query')
    # search title, tags, content
    # how to order results?
    return 'paged search page with results from search'
