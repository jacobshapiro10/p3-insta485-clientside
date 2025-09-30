"""REST API for posts."""
import flask
import insta485
import hashlib

def check_credentials():
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



@insta485.app.route('/api/v1/')
def get_api_root():
  context = {
  "comments": "/api/v1/comments/",
  "likes": "/api/v1/likes/",
  "posts": "/api/v1/posts/",
  "url": "/api/v1/"
}
  return flask.jsonify(**context)



  

  posts = [
    {"postid": row["postid"], "url": f"/api/v1/posts/{row['postid']}/"}
    for row in money
  ]

  return flask.jsonify({
    "next": "",
    "results": posts,
    "url": "/api/v1/posts/"
  })

@insta485.app.route('/api/v1/posts/')
def show_posts():
  username = check_credentials()
  connection = insta485.model.get_db()
  if username is None:
    return flask.jsonify({
            "message": "Forbidden",
            "status_code": 403
        }), 403


  N = flask.request.args.get("postid_lte", type=int)

  if N is None:
    row = connection.execute("SELECT MAX(postid) AS max_id FROM posts").fetchone()
    N = row["max_id"]



 
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
    LIMIT 10
    """,
    (username, username, N)
  ).fetchall()
    

  posts = [
    {"postid": row["postid"], "url": f"/api/v1/posts/{row['postid']}/"}
    for row in money
  ]

  return flask.jsonify({
    "next": "",
    "results": posts,
    "url": "/api/v1/posts/"
  })
  



    




@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
  username = check_credentials()
  if username is None:
    return flask.jsonify({
            "message": "Forbidden",
            "status_code": 403
        }), 403

  context = {
      "created": "2017-09-28 04:33:28",
      "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
      "owner": "awdeorio",
      "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
      "ownerShowUrl": "/users/awdeorio/",
      "postShowUrl": f"/posts/{postid_url_slug}/",
      "postid": postid_url_slug,
      "url": flask.request.path,
  }
  return flask.jsonify(**context)



