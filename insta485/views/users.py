"""User profile and related views."""
import flask
from flask import abort

import insta485


@insta485.app.route('/users/<username>/')
def show_user(username):
    """Show user profile page.

    :type username: str
    :param username: The username of the profile to display

    :raises: 404 if the user does not exist

    :rtype: flask.Response
    :returns: Rendered user profile page
    """
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login_get'))
    logname = flask.session["username"]

    connection = insta485.model.get_db()

    qc = connection.execute(
        """
        SELECT 1 AS username_exists
        FROM users AS u WHERE u.username = ?
        """,
        (username,)
    ).fetchone()

    if qc is None:
        abort(404)

    info = connection.execute(
        """
        SELECT 1 AS does_loguser_follow_username
        FROM following AS f WHERE f.follower = ?
        AND f.followee = ?
        """,
        (logname, username)
    ).fetchone()

    if info is None:
        loguser_follows_username = False
    else:
        loguser_follows_username = True

    num_posts = connection.execute(
        """
        SELECT COUNT(*) AS num_posts
        FROM posts AS p
        WHERE owner = ?

        """,
        (username,)
    ).fetchone()['num_posts']

    num_followers = connection.execute(
        """
        SELECT COUNT(follower) AS numfollowers
        FROM following AS f
        WHERE f.followee = ?
        """,
        (username,)
    ).fetchone()['numfollowers']

    num_following = connection.execute(
        """
        SELECT COUNT(followee) AS numfollowees
        FROM following AS f
        WHERE f.follower = ?

        """,
        (username,)
    ).fetchone()['numfollowees']

    name = connection.execute(
        """
        SELECT fullname AS name
        FROM users AS u
        WHERE u.username = ?
        """,
        (username,)
    ).fetchone()['name']

    posts_info = connection.execute(
        """
        SELECT postid, filename
        FROM posts
        WHERE owner = ?
        ORDER BY postid DESC
        """,
        (username,)
    ).fetchall()

    context = {
        "logname": logname,
        "username": username,
        "does_logname_follow_user": loguser_follows_username,
        "num_posts": num_posts,
        "num_followers": num_followers,
        "num_following": num_following,
        "fullname": name,
        "posts": posts_info,
    }

    return flask.render_template("users.html", **context)


@insta485.app.route('/users/<username>/followers/')
def show_user_followers(username):
    """Show user followers page.

    :type username: str
    :param username: The username of the profile to display

    :raises: 404 if the user does not exist

    :rtype: flask.Response
    :returns: Rendered user followers page
    """
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login_get'))
    logname = flask.session["username"]

    connection = insta485.model.get_db()

    fault = connection.execute(
        """
        SELECT 1 FROM users AS u
        WHERE u.username = ?
        """,
        (username,)
    ).fetchone()

    if fault is None:
        abort(404)

    cur = connection.execute(
        """
        SELECT u.username, u.filename AS user_pic
        FROM following AS f
        JOIN users AS u ON f.follower = u.username
        WHERE f.followee = ?
        """,
        (username,)
    )
    followers = cur.fetchall()

    for follower in followers:
        if follower["username"] == logname:
            follower["relationship"] = "self"
        else:
            check = connection.execute(
                """
                SELECT 1 FROM following
                WHERE follower = ? AND followee = ?
                """,
                (logname, follower["username"])
            ).fetchone()

            if check is None:
                follower["relationship"] = "not_following"
            else:
                follower["relationship"] = "following"

    context = {"username": username, "logname": logname,
               "followers": followers}

    return flask.render_template("user_followers.html", **context)


@insta485.app.route('/users/<username>/following/')
def show_user_following(username):
    """Show user following page.

    :type username: str
    :param username: The username of the profile to display

    :raises: 404 if the user does not exist

    :rtype: flask.Response
    :returns: Rendered user following page
    """
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login_get'))
    logname = flask.session["username"]

    connection = insta485.model.get_db()

    fault = connection.execute(
        """
        SELECT 1 FROM users AS u
        WHERE u.username = ?
        """,
        (username,)
    ).fetchone()

    if fault is None:
        abort(404)

    cur = connection.execute(
        """
        SELECT u.username, u.filename AS user_pic
        FROM following AS f
        JOIN users AS u ON f.followee = u.username
        WHERE f.follower = ?
        """,
        (username,)
    )
    following = cur.fetchall()

    for followee in following:
        if followee["username"] == logname:
            followee["relationship"] = "self"
        else:
            check = connection.execute(
                """
                SELECT 1 FROM following
                WHERE follower = ? AND followee = ?
                """,
                (logname, followee["username"])
            ).fetchone()

            if check is None:
                followee["relationship"] = "not_following"
            else:
                followee["relationship"] = "following"

    context = {"username": username, "logname": logname,
               "following": following}
    return flask.render_template("user_following.html", **context)
