import sqlite3

import click
from flask_sqlalchemy import SQLAlchemy

from flask import current_app
from flask import g
from flask.cli import with_appcontext

db = SQLAlchemy()

def get_db():
    if "db" not in g:
        g.db = db
    # TODO: figure out when we should really be calling init_app.  in __init__ or here.
    return g.db


def close_db(e=None):
    db = g.pop("db", None)

def init_db():
    """Clear existing data and create new tables."""
    db = get_db()
    with current_app.app_context():
        db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
