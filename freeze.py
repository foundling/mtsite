from flask_frozen import Freezer
from app import app

from shutil import rmtree


freezer = Freezer(app)


if __name__ == '__main__':
    freezer.freeze()
