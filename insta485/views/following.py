"""Follow and unfollow a user view."""
import flask

import insta485


@insta485.app.route('/following/', methods=["POST"])
def update_following():
    """Update following status of a user.

    :raises: 403 for forbidden actions, 400 for bad requests,
                409 for conflicts

    :rtype: flask.Response
    :returns: Redirect to the target page after operation
    """
    print("followers parameter")
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login_get'))
    operation = flask.request.form["operation"]
    username = flask.request.form["username"]  # The second user
    logname = flask.session["username"]
    connection = insta485.model.get_db()

    # Follows users
    if operation == "follow":

        # If a user tries to follow a user that they already follow
        # then abort(409).
        # Check if already following
        res = connection.execute(
            "SELECT 1 FROM following WHERE follower=? AND followee=?",
            (logname, username)
        ).fetchone()
        if res is not None:
            flask.abort(409)

        connection.execute(
            "INSERT INTO following(follower, followee) VALUES (?, ?)",
            (logname, username)
        )

    # Unfollows user
    elif operation == "unfollow":

        # If a user tries to unfollow a user that they
        # do not follow, then abort(409).
        res = connection.execute(
            "SELECT 1 FROM following WHERE follower=? AND followee=?",
            (logname, username)
        ).fetchone()
        if res is None:
            flask.abort(409)

        connection.execute(
            "DELETE FROM following WHERE follower=? AND followee=?",
            (logname, username)
        )
    else:
        flask.abort(400)

    target = flask.request.args.get("target", "/")
    return flask.redirect(target)
