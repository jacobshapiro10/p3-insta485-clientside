"""Posts get and post view functions."""
import os
import pathlib
import uuid

import flask

import insta485


@insta485.app.route('/posts/<int:postid>/')
def show_post(postid):
    """Display a specific post and its comments.

    :type postid: int
    :param postid: The ID of the post to display

    :raises: 404 if the post does not exist

    :rtype: flask.Response
    :returns: Rendered post page
    """
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login_get'))
    logname = flask.session["username"]

    # Connect to database
    connection = insta485.model.get_db()

    cur = connection.execute(
        """
        SELECT p.postid, p.filename, p.owner, p.created,
        u.filename AS owner_pic
        FROM posts p JOIN users u ON p.owner = u.username
        WHERE p.postid = ?
        """,
        (postid,)
    )

    post = cur.fetchone()  # only for one post

    if post is None:
        # If no post with this id, return 404
        flask.abort(404)

    # Get all comments for this post
    # cur = connection.execute(
    #     """
    #     SELECT owner, text, commentid  -- add commentid if you need it
    #     FROM comments
    #     WHERE postid = ?
    #     ORDER BY created ASC;
    #     """,
    #     (post[postid_url_slug],)
    # )

    # post["comments"] = cur.fetchall()

    # Query for all comments on the post
    cursor = connection.execute(
        """
        SELECT c.commentid, c.text, c.owner, c.created, u.filename
        FROM comments c JOIN users u ON c.owner = u.username
        WHERE c.postid = ?
        ORDER BY c.commentid ASC
        """,
        (postid,)
    )

    comments = cursor.fetchall()

    # Query for the like count on the post
    cursor = connection.execute(
        "SELECT COUNT(*) AS count FROM likes WHERE postid = ?",
        (postid,)
    )
    like_count = cursor.fetchone()['count']

    # Check if the logged-in user liked this post
    # cur = connection.execute(
    #     """
    #     SELECT 1
    #     FROM likes
    #     WHERE owner = ?
    #     AND postid = ?;
    #     """,
    #     (logname, post['postid'])
    # )
    # if cur.fetchone() is None:
    #     post["logname_likes_post"] = False
    # else:
    #     post["logname_likes_post"] = True

    # Check if the logged-in user has liked the post
    cursor = connection.execute(
        "SELECT COUNT(*) AS count FROM likes WHERE postid = ? AND owner = ?",
        (postid, logname)
    )
    is_liked_by_user = cursor.fetchone()['count'] > 0

    # --- Prepare context for the template ---
    context = {
        'post': post,
        "comments": comments,
        "like_count": like_count,
        "is_liked_by_user": is_liked_by_user,
        "logname": logname
    }

    # --- Render and return the template ---
    return flask.render_template("post.html", **context)


@insta485.app.route('/posts/', methods=['POST'])
def update_posts():
    """Handle post creation and deletion.

    :raises: 403 if the user is not authorized to delete the post
             400 if no file is provided for upload

    :rtype: flask.Response
    :returns: Redirect to the target page after operation
    """
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login_get'))

    operation = flask.request.form["operation"]
    logname = flask.session["username"]
    connection = insta485.model.get_db()

    if operation == "create":
        fileobj = flask.request.files["file"]
        filename = fileobj.filename

        if not filename:
            flask.abort(400)

        # Compute base name (filename without directory). We use a UUID to
        # avoid clashes with existing files, and ensure that the name is
        # compatible with the filesystem. For best practive, we ensure
        # uniform file extensions (e.g. lowercase).

        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        connection.execute(
            "INSERT INTO posts(filename, owner) VALUES (?, ?)",
            (uuid_basename, logname)
        )

    elif operation == "delete":

        postid = flask.request.form["postid"]

        # Get owner and filename from database
        post_info = connection.execute(
            "SELECT owner, filename FROM posts WHERE postid=?",
            (postid,)
        ).fetchone()
        if post_info is None or post_info["owner"] != logname:
            flask.abort(403)
        filename = post_info["filename"]

        # Delete related likes and comments
        connection.execute(
            "DELETE FROM comments WHERE postid=?",
            (postid,)
        )
        connection.execute(
            "DELETE FROM likes WHERE postid=?",
            (postid,)
        )
        # Delete post
        connection.execute(
            "DELETE FROM posts WHERE postid=?",
            (postid,)
        )

        # Remove image file from filesystem
        path = insta485.app.config["UPLOAD_FOLDER"] / filename
        if os.path.exists(path):
            os.remove(path)

    target = flask.request.args.get("target", f"/users/{logname}/")
    return flask.redirect(target)
