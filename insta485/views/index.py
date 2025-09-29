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
    """Show the main index page ("/").

    :raises: 403 if user not logged in

    :rtype: flask.Response
    :returns: Redirect to login page if not logged in,
                otherwise render index.html
    """
    # Connect to database
    connection = insta485.model.get_db()

    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login_get'))

    logname = flask.session["username"]

    cur = connection.execute(
        """
        SELECT p.postid,
       p.owner AS owner,
       u.filename AS owner_pic,
       p.filename AS post_file,
       p.created AS creation_date,
       COUNT(DISTINCT l.likeid) AS like_count
    FROM posts AS p
    JOIN users AS u ON p.owner = u.username
    LEFT JOIN likes AS l ON p.postid = l.postid
    WHERE p.owner = ?
    OR p.owner IN (
        SELECT f.followee
        FROM following AS f
        WHERE f.follower = ?
    )
    GROUP BY p.postid, p.owner, u.filename, p.filename, p.created
    ORDER BY p.postid DESC;
        """,

        (logname, logname)
    )

    posts = cur.fetchall()

    for post in posts:
        dt = arrow.get(post['creation_date'])
        post['created_human'] = dt.humanize()
        cur = connection.execute(
            """

            SELECT owner, text
            FROM comments
            WHERE postid = ?
            ORDER BY created ASC;
            """,
            (post["postid"],)
        )
        post["comments"] = cur.fetchall()

        ano = connection.execute(
            """

            SELECT 1
            FROM likes
            WHERE owner = ?
            AND postid = ?;
            """,
            (logname, post['postid'])
        )

        anot = ano.fetchone()

        if anot is None:
            post["logname_likes_post"] = False
        else:
            post["logname_likes_post"] = True

    context = {"posts": posts, "logname": logname}
    return flask.render_template("index.html", **context)
