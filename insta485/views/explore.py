"""Explore page view."""
import flask

import insta485


@insta485.app.route('/explore/')
def show_explore():
    """Show explore page.

    :raises: 403 if user not logged in

    :rtype: flask.Response
    :returns: Rendered explore page
    """
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login_get'))
    logname = flask.session["username"]

    connection = insta485.model.get_db()

    info = connection.execute(
        """
        SELECT u.username, u.filename
        FROM users AS u
        WHERE u.username != ?
            AND u.username NOT IN (
                SELECT f.followee
                FROM following AS f
                WHERE f.follower = ?
            )
        """, (logname, logname)
    ).fetchall()

    context = {"logname": logname, "user_info": info}

    return flask.render_template("explore.html", **context)
