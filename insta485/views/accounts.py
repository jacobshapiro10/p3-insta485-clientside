"""Views for accounts-related routes."""
import hashlib
import pathlib
import uuid

import flask
from flask import abort

import insta485
from insta485 import app


@app.route('/accounts/login/')
def login_get():
    """Login page view.

    :raises: no username found in session

    :rtype: flask.Response
    :returns: Rendered login page
    """
    if "username" in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("accounts_login.html")


@app.route('/accounts/create/')
def create_account():
    """Create account page view.

    :raises: no username found in session

    :rtype: flask.Response
    :returns: Rendered create account page
    """
    if "username" in flask.session:
        return flask.redirect(flask.url_for('edit_account'))
    return flask.render_template("accounts_create.html")


@app.route('/accounts/edit/')
def edit_account():
    """Account edit page view.

    :raises: no username found in session

    :rtype: flask.Response
    :returns: Rendered edit account page
    """
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login_get'))
    logname = flask.session["username"]
    connection = insta485.model.get_db()
    info = connection.execute(
        """
        SELECT username, email, fullname, filename
        FROM users AS u
        WHERE u.username = ?

        """,
        (logname,)

    ).fetchall()

    context = {"info": info}

    return flask.render_template("accounts_edit.html", **context)


@app.route('/accounts/delete/')
def delete_account():
    """Delete account page view.

    :raises: no username found in session

    :rtype: flask.Response
    :returns: Rendered delete account page
    """
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login_get'))
    logname = flask.session["username"]
    context = {"logname": logname}
    return flask.render_template("accounts_delete.html", **context)


@app.route('/accounts/auth/')
def authenticate_account():
    """Authenticate check endpoint.

    :raises: no username found in session

    :rtype: flask.Response
    :returns: Empty 200 response if authenticated
    """
    if "username" not in flask.session:
        abort(403)
    return ("", 200)


@app.route('/accounts/password/')
def change_password():
    """Change password page view.

    :raises: no username found in session

    :rtype: flask.Response
    :returns: Rendered change password page
    """
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login_get'))
    logname = flask.session["username"]
    context = {"logname": logname}
    return flask.render_template("change_password.html", **context)


@app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Logout endpoint.

    :raises: no username found in session

    :rtype: flask.Response
    :returns: Redirect to login page after logout
    """
    flask.session.clear()
    return flask.redirect(flask.url_for('login_get'))


@app.route('/accounts/', methods=['POST'])
def account_operations():
    """Handle various account operations.

    :raises: 403 for forbidden actions, 400 for bad requests,
                409 for conflicts, 401 for unauthorized actions

    :rtype: flask.Response
    :returns: Redirect to the target page after operation
    """
    operation = flask.request.form["operation"]
    if operation == "login":
        connection = insta485.model.get_db()
        username = flask.request.form['username']
        password = flask.request.form['password']
        if not username or not password:
            abort(400)

        user = connection.execute(
            "SELECT password FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            abort(403)

        algorithm, salt, stored_hash = user["password"].split("$")

        hash_obj = hashlib.new(algorithm)
        hash_obj.update((salt + password).encode("utf-8"))
        computed_hash = hash_obj.hexdigest()

        if computed_hash != stored_hash:
            abort(403)

        flask.session['username'] = username

        target = flask.request.args.get("target", "/")
        return flask.redirect(target)

    elif operation == "create":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        fullname = flask.request.form["fullname"]
        email = flask.request.form["email"]
        fileobj = flask.request.files["file"]

        if username is None:
            abort(400)
        elif password is None:
            abort(400)
        elif fullname is None:
            abort(400)
        elif email is None:
            abort(400)
        elif fileobj is None:
            abort(400)

        connection = insta485.model.get_db()

        info = connection.execute(
            """
            SELECT 1 FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        if info is not None:
            abort(409)

        algorithm = 'sha512'
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])
        print(password_db_string)

        stem = uuid.uuid4().hex
        suffix = pathlib.Path(fileobj.filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"
        filepath = app.config["UPLOAD_FOLDER"] / uuid_basename
        fileobj.save(filepath)

        connection.execute(
            """INSERT INTO users(username, fullname, email, filename, password)
            VALUES (?, ?, ?, ?, ?)""",
            (username, fullname, email, uuid_basename, password_db_string)
        )

        flask.session['username'] = username

        target = flask.request.args.get("target", "/")
        return flask.redirect(target)

    elif operation == "delete":
        if "username" not in flask.session:
            abort(403)
        connection = insta485.model.get_db()

        row = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (flask.session["username"],)
        ).fetchone()

        if row:
            filepath = app.config["UPLOAD_FOLDER"] / row["filename"]
            if filepath.is_file():
                filepath.unlink()

        rows = connection.execute(
            "SELECT filename FROM posts WHERE owner = ?",
            (flask.session["username"],)
        ).fetchall()
        for r in rows:
            filepath = app.config["UPLOAD_FOLDER"] / r["filename"]
            if filepath.is_file():
                filepath.unlink()
        connection.execute(
            "DELETE FROM users WHERE username = ?",
            (flask.session["username"],)
        )
        flask.session.clear()
        target = flask.request.args.get("target", "/")
        return flask.redirect(target)

    elif operation == "edit_account":
        if "username" not in flask.session:
            abort(403)
        username = flask.session["username"]
        fullname = flask.request.form["fullname"]
        email = flask.request.form["email"]
        fileobj = flask.request.files["file"]

        if not fullname or not email:
            abort(400)
        connection = insta485.model.get_db()

        if fileobj and fileobj.filename:
            row = connection.execute(
                "SELECT filename FROM users WHERE username = ?",
                (flask.session["username"],)
            ).fetchone()

            if row:
                filepath = app.config["UPLOAD_FOLDER"] / row["filename"]
                if filepath.is_file():
                    filepath.unlink()

            stem = uuid.uuid4().hex
            suffix = pathlib.Path(fileobj.filename).suffix.lower()
            uuid_basename = f"{stem}{suffix}"
            filepath = app.config["UPLOAD_FOLDER"] / uuid_basename
            fileobj.save(filepath)

            connection.execute(
                """UPDATE users SET email = ?, fullname = ?, filename = ?
                WHERE username = ?""",
                (email, fullname, uuid_basename, username)
            )

        else:
            connection.execute(
                "UPDATE users SET email = ?, fullname = ? WHERE username = ?",
                (email, fullname, username)
            )

        target = flask.request.args.get("target", "/")
        return flask.redirect(target)

    elif operation == "update_password":
        connection = insta485.model.get_db()
        if "username" not in flask.session:
            abort(403)
        old_password = flask.request.form["password"]
        new_password = flask.request.form["new_password1"]
        confirmation_password = flask.request.form["new_password2"]
        username = flask.session["username"]

        if not old_password or not new_password or not confirmation_password:
            abort(400)

        user = connection.execute(
            "SELECT password FROM users WHERE username = ?", (username,)
        ).fetchone()

        algorithm, salt, stored_hash = user["password"].split("$")

        hash_obj = hashlib.new(algorithm)
        hash_obj.update((salt + old_password).encode("utf-8"))
        computed_hash = hash_obj.hexdigest()

        if computed_hash != stored_hash:
            abort(403)

        if new_password != confirmation_password:
            abort(401)

        algorithm = 'sha512'
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + new_password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string1 = "$".join([algorithm, salt, password_hash])

        connection.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (password_db_string1, username)
            )

        target = flask.request.args.get("target", "/")
        return flask.redirect(target)
