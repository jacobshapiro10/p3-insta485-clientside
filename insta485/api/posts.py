"""REST API for posts."""
import flask
import insta485
import hashlib



@insta485.app.route('/api/v1/')
def get_api_root():
  context = {
  "comments": "/api/v1/comments/",
  "likes": "/api/v1/likes/",
  "posts": "/api/v1/posts/",
  "url": "/api/v1/"
}
  return flask.jsonify(**context)

"""
@insta485.app.route('/api/v1/posts/')
def show_posts():

"""
  


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
  auth = flask.request.authorization

  if auth is None:
      return flask.jsonify({
          "message": "Forbidden",
          "status_code": 403
      }), 403

  username = auth.username
  password = auth.password

  connection = insta485.model.get_db()
  user = connection.execute(
    "SELECT password FROM users WHERE username = ?", (username,)
  ).fetchone()

  if user is None:
    return flask.jsonify({
          "message": "Forbidden",
          "status_code": 403
      }), 403

  algorithm, salt, stored_hash = user["password"].split("$")

  hash_obj = hashlib.new(algorithm)
  hash_obj.update((salt + password).encode("utf-8"))
  computed_hash = hash_obj.hexdigest()

  if computed_hash != stored_hash:
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
