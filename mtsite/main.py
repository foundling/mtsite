from flask import Blueprint, request

main = Blueprint('main', __name__)

# content for main page

@main.route('/')
def index():
    render_template('index.html')

@main.route('/search')
def search_blog():
    search_query = request.args.get('query')
    # search title, tags, content
    # how to order results?
    return 'paged search page with results from search'
