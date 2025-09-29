"""Like and unlike a post view."""
import flask
from flask import abort

import insta485

LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route("/likes/", methods=["POST"])
def update_likes():
    """Update likes on a post.

    :raises: 403 for forbidden actions, 409 for conflicts

    :rtype: flask.Response
    :returns: Redirect to the target page after operationß
    """
    LOGGER.debug("operation = %s", flask.request.form["operation"])
    LOGGER.debug("postid = %s", flask.request.form["postid"])
    operation = flask.request.form["operation"]
    connection = insta485.model.get_db()
    if operation == "unlike":
        important_info = connection.execute(
            """
            SELECT 1 FROM likes
            WHERE owner = ?
            AND postid = ?
            """,
            (flask.session["username"], flask.request.form["postid"])
        ).fetchone()

        if important_info is None:
            abort(409)
        connection.execute(
            """
            DELETE FROM likes
            WHERE owner = ?
            AND postid = ?
            """,
            (flask.session["username"], flask.request.form["postid"])
        )
    else:
        important_info = connection.execute(
            """
            SELECT 1 FROM likes
            WHERE owner = ?
            AND postid = ?
            """,
            (flask.session["username"], flask.request.form["postid"])
        ).fetchone()

        if important_info is not None:
            abort(409)
        connection.execute(
            "INSERT INTO likes(owner, postid) VALUES (?, ?)",
            (flask.session["username"], flask.request.form["postid"])
        )

    target = flask.request.args.get("target", "/")
    return flask.redirect(target)
