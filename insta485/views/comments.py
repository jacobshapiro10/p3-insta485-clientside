"""Add or delete a comment view."""
import flask
from flask import abort

import insta485


@insta485.app.route('/comments/', methods=["POST"])
def add_comment():
    """Add or delete a comment.

    :raises: 403 for forbidden actions, 400 for bad requests

    :rtype: flask.Response
    :returns: Redirect to the target page after operation
    """
    operation = flask.request.form["operation"]
    connection = insta485.model.get_db()
    if operation == "create":
        postid = flask.request.form["postid"]
        text = flask.request.form["text"]
        if not text:
            abort(400)
        connection.execute(
            "INSERT INTO comments(owner, postid, text) VALUES (?, ?, ?)",
            (flask.session["username"], postid, text)
        )
    else:
        commentid = flask.request.form["commentid"]
        row = connection.execute(
            "SELECT owner FROM comments WHERE commentid=?",
            (commentid,)
        ).fetchone()

        if row["owner"] != flask.session["username"]:
            flask.abort(403)

        connection.execute(
            "DELETE FROM comments WHERE commentid = ?",
            (commentid, )
        )
    target = flask.request.args.get("target", "/")
    return flask.redirect(target)
