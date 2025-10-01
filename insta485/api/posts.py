"""REST API for posts."""
import flask
import insta485
import hashlib
from urllib.parse import urlencode


def check_credentials():
    """Return username if credentials are valid, else None."""
    connection = insta485.model.get_db()
    auth = flask.request.authorization

    # Case 1: Basic Auth
    if auth:
        username = auth.username
        password = auth.password
        user = connection.execute(
            "SELECT password FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user is None:
            return None

        algorithm, salt, stored_hash = user["password"].split("$")
        hash_obj = hashlib.new(algorithm)
        hash_obj.update((salt + password).encode("utf-8"))
        if hash_obj.hexdigest() != stored_hash:
            return None

        return username

    # Case 2: Session cookie
    if "username" in flask.session:
        return flask.session["username"]

    return None


@insta485.app.route("/api/v1/")
def get_api_root():
    """API root resource listing."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/",
    }
    return flask.jsonify(**context)


@insta485.app.route("/api/v1/posts/")
def show_posts():
    """Return paginated posts for the logged-in user or followees."""
    username = check_credentials()
    connection = insta485.model.get_db()
    if username is None:
        return flask.jsonify({
            "message": "Forbidden",
            "status_code": 403
        }), 403

    # Parse query params
    origN = flask.request.args.get("postid_lte", type=int)
    origSize = flask.request.args.get("size", type=int)
    origPage = flask.request.args.get("page", type=int)

    # Defaults
    size = origSize if origSize is not None else 10
    page = origPage if origPage is not None else 0
    if origN is None:
        row = connection.execute("SELECT MAX(postid) AS max_id FROM posts").fetchone()
        N = row["max_id"]
    else:
        N = origN

 
    if size <= 0 or page < 0:
        return flask.jsonify({
            "message": "Bad Request",
            "status_code": 400
        }), 400

    # Query posts
    money = connection.execute(
        """
        SELECT p.postid,
              p.filename,
              p.owner,
              p.created
        FROM posts AS p
        WHERE (p.owner = ?
          OR p.owner IN (
            SELECT f.followee
            FROM following AS f
            WHERE f.follower = ?
          ))
        AND p.postid <= ?
        ORDER BY p.postid DESC
        LIMIT ? OFFSET ?
        """,
        (username, username, N, size, size * page)
    ).fetchall()

    posts = [
        {"postid": row["postid"], "url": f"/api/v1/posts/{row['postid']}/"}
        for row in money
    ]

    params = {}
    if origSize is not None:
      params["size"] = origSize
    if origPage is not None:
      params["page"] = origPage
    if origN is not None:
      params["postid_lte"] = origN
    
    
    url = "/api/v1/posts/"
    if params:
        url += "?" + urlencode(params)

   
    next_url = ""
    if len(posts) == size:
      last_seen_postid = posts[0]["postid"]
      next_url = f"/api/v1/posts/?size={size}&page={page+1}&postid_lte={last_seen_postid}"

    return flask.jsonify({
        "next": next_url,
        "results": posts,
        "url": url
    })


@insta485.app.route("/api/v1/posts/<int:postid_url_slug>/")
def get_post(postid_url_slug):
    """Return details of a single post, or 404 if not found."""
    username = check_credentials()
    if username is None:
        return flask.jsonify({
            "message": "Forbidden",
            "status_code": 403
        }), 403

    connection = insta485.model.get_db()
    row = connection.execute(
        "SELECT * FROM posts WHERE postid = ?", (postid_url_slug,)
    ).fetchone()

    if row is None:
        return flask.jsonify({
            "message": "Not Found",
            "status_code": 404
        }), 404

    # context = {
    #     "created": row["created"],
    #     "imgUrl": f"/uploads/{row['filename']}",
    #     "owner": row["owner"],
    #     # Dummy owner image / show URL since schema doesn’t hold it
    #     "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
    #     "ownerShowUrl": f"/users/{row['owner']}/",
    #     "postShowUrl": f"/posts/{postid_url_slug}/",
    #     "postid": row["postid"],
    #     "url": flask.request.path,
    # }
    # return flask.jsonify(**context)

        # --- Fetch comments ---
    comments = connection.execute(
        """
        SELECT commentid, owner, text
        FROM comments
        WHERE postid = ?
        ORDER BY commentid ASC
        """,
        (postid_url_slug,)
    ).fetchall()

    comment_list = [
        {
            "commentid": c["commentid"],
            "lognameOwnsThis": (c["owner"] == username),
            "owner": c["owner"],
            "ownerShowUrl": f"/users/{c['owner']}/",
            "text": c["text"],
            "url": f"/api/v1/comments/{c['commentid']}/"
        }
        for c in comments
    ]

    # --- Fetch likes ---
    likes_row = connection.execute(
        "SELECT COUNT(*) AS count FROM likes WHERE postid = ?",
        (postid_url_slug,)
    ).fetchone()
    num_likes = likes_row["count"]

    user_like = connection.execute(
        "SELECT likeid FROM likes WHERE postid = ? AND owner = ?",
        (postid_url_slug, username)
    ).fetchone()

    likes_obj = {
        "lognameLikesThis": user_like is not None,
        "numLikes": num_likes,
        "url": f"/api/v1/likes/{user_like['likeid']}/" if user_like else None
    }

    # --- Build response ---
    context = {
        "comments": comment_list,
        "comments_url": f"/api/v1/comments/?postid={postid_url_slug}",
        "created": row["created"],
        "imgUrl": f"/uploads/{row['filename']}",
        "likes": likes_obj,
        "owner": row["owner"],
        # "ownerImgUrl": f"/uploads/{row['owner']}.jpg",  # TODO: replace with actual profile filename query if needed
        "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
        "ownerShowUrl": f"/users/{row['owner']}/",
        "postShowUrl": f"/posts/{postid_url_slug}/",
        "postid": row["postid"],
        "url": flask.request.path,
    }

    return flask.jsonify(**context)


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def create_like():
    """Handle likes on a post."""
    username = check_credentials()
    if username is None:
        return flask.jsonify({
            "message": "Forbidden",
            "status_code": 403
        }), 403

    db = insta485.model.get_db()

    # Parse postid from query parameter
    postid = flask.request.args.get("postid", type=int)
    if postid is None:
        return flask.jsonify({"message": "Missing postid"}), 400

    # Make sure post exists
    # Post IDs that are out of range should return a 404 error.
    post = db.execute(
        "SELECT postid FROM posts WHERE postid=?",
        (postid,)
    ).fetchone()
    if post is None:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404

    # If the “like” already exists, return the like object with a 200 response
    row = db.execute(
        "SELECT likeid FROM likes WHERE postid=? AND owner=?",
        (postid, username)
    ).fetchone()
    if row:
        return flask.jsonify({"likeid": row["likeid"], 
          "url": f"/api/v1/likes/{row['likeid']}/"}), 200

    # Create one “like” for a specific post. Return 201 on success.
    db.execute(
        "INSERT INTO likes(owner, postid) VALUES (?, ?)",
        (username, postid)
    )
    likeid = db.execute(
        "SELECT last_insert_rowid() AS lid"
    ).fetchone()["lid"]
    return flask.jsonify({"likeid": likeid, "url": f"/api/v1/likes/{likeid}/"}), 201


@insta485.app.route('/api/v1/likes/<int:like_id>/', methods=['DELETE'])
def delete_like(like_id):
    """Handle lkes on a post."""
    # Check user is authenticated
    username = check_credentials()
    if username is None:
        return flask.jsonify({
            "message": "Forbidden",
            "status_code": 403
        }), 403

    db = insta485.model.get_db()

    # If the “like_id” doesn't exists, return 404
    row = db.execute(
        "SELECT likeid FROM likes WHERE likeid=?",
        (like_id,)
    ).fetchone()
    if not row:
        return flask.jsonify({
            "message": "likeid Not Found",
            "status_code": 404
        }), 404

    # If the user does not own the “like” return 403
    row = db.execute(
        "SELECT likeid FROM likes WHERE likeid=? AND owner=?",
        (like_id, username)
    ).fetchone()
    if not row:
        return flask.jsonify({
            "message": "User does not own likeid",
            "status_code": 403
        }), 403

    # Delete one “like” for a specific post. Return 204 on success.
    db.execute(
        "DELETE FROM likes WHERE likeid=?", (like_id,)
    )
    return "", 204


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def create_comment():
    """Handle comments on a post."""
    username = check_credentials()
    if username is None:
        return flask.jsonify({
            "message": "Forbidden",
            "status_code": 403
        }), 403

    db = insta485.model.get_db()

    # Parse postid from query parameter
    postid = flask.request.args.get("postid", type=int)
    if postid is None:
        return flask.jsonify({"message": "Missing postid"}), 400

    # Make sure post exists
    # Post IDs that are out of range should return a 404 error.
    post = db.execute(
        "SELECT postid FROM posts WHERE postid=?",
        (postid,)
    ).fetchone()
    if post is None:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404

    # Get comment text from JSON body
    body = flask.request.get_json(silent=True)
    if not body or "text" not in body:
        return flask.jsonify({
            "message": "Missing text field",
            "status_code": 400
        }), 400
    text = body["text"].strip()
    if not text:
        return flask.jsonify({
            "message": "Empty comment not allowed",
            "status_code": 400
        }), 400
    
    # Create one comment for a specific post. Return 201 on success.
    db.execute(
        "INSERT INTO comments(owner, postid, text) VALUES (?, ?, ?)",
        (username, postid, text)
    )
    commentid = db.execute(
        "SELECT last_insert_rowid() AS lid"
    ).fetchone()["lid"]
    return flask.jsonify({"commentid": commentid, "url": f"/api/v1/comments/{commentid}/"}), 201



@insta485.app.route('/api/v1/comments/<int:comment_id>/', methods=['DELETE'])
def delete_comment(comment_id):
    """Handle lkes on a post."""
    # Check user is authenticated
    username = check_credentials()
    if username is None:
        return flask.jsonify({
            "message": "Forbidden",
            "status_code": 403
        }), 403

    db = insta485.model.get_db()

    # If the “comment_id” doesn't exists, return 404
    row = db.execute(
        "SELECT commentid FROM comments WHERE commentid=?",
        (comment_id,)
    ).fetchone()
    if not row:
        return flask.jsonify({
            "message": "commentid Not Found",
            "status_code": 404
        }), 404

    # If the user does not own the "comments" return 403
    row = db.execute(
        "SELECT commentid FROM comments WHERE commentid=? AND owner=?",
        (comment_id, username)
    ).fetchone()
    if not row:
        return flask.jsonify({
            "message": "User does not own commentid",
            "status_code": 403
        }), 403

    # Delete one “comments” for a specific post. Return 204 on success.
    db.execute(
        "DELETE FROM comments WHERE commentid=?", (comment_id,)
    )
    return "", 204
