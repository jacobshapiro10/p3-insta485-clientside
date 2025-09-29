"""Serve uploaded files view."""
import flask
from flask import abort

import insta485


@insta485.app.route("/uploads/<filename>")
def upload_file(filename):
    """Serve uploaded files.

    :type filename: str
    :param filename: The name of the file to serve

    :raises: 403 if user not logged in, 404 if file not found

    :rtype: flask.Response
    :returns: The requested file
    """
    if "username" not in flask.session:
        abort(403)

    filepath = insta485.app.config["UPLOAD_FOLDER"] / filename

    if not filepath.is_file():
        flask.abort(404)

    return flask.send_from_directory(
        insta485.app.config["UPLOAD_FOLDER"], filename
    )
