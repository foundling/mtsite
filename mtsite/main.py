from flask import Blueprint, request, render_template

main = Blueprint('main', __name__)

# content for main page

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/search')
def search_blog():
    print(request.args)
    search_query = request.args
    # search title, tags, content
    # how to order results?
    return 'search query: {}'.format(str(search_query))
