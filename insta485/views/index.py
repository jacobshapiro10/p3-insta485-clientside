"""
Insta485 index (main) view.

URLs include:
/
"""
import arrow
import flask

import insta485


@insta485.app.route('/')
def show_index():
    """Display the main (index) page."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login_get'))
    return flask.render_template(
        "index.html", logname=flask.session["username"]
    )
