from flask import Blueprint, render_template

bp = Blueprint('main', __name__, template_folder='templates', static_folder='static', static_url_path='/main/static')

@bp.route('/')
def index():
    return render_template('main/index.html')
