"""Insta485 package initializer."""
import secrets
import uuid

import flask
from flask_wtf.csrf import CSRFProtect

# app is a single object used by all the code modules in this package
app = flask.Flask(__name__)  # pylint: disable=invalid-name

# Read settings from config module (insta485/config.py)
app.config.from_object('insta485.config')

# Overlay settings read from a Python file whose path is set in the environment
# variable INSTA485_SETTINGS. Setting this environment variable is optional.
# Docs: http://flask.pocoo.org/docs/latest/config/
#
# EXAMPLE:
# $ export INSTA485_SETTINGS=secret_key_config.py
app.config.from_envvar('INSTA485_SETTINGS', silent=True)

# generate a CSRF token
csrf = CSRFProtect()
csrf.init_app(app)

import insta485.api  # noqa: E402  pylint: disable=wrong-import-position


import insta485.model  # noqa: E402  pylint: disable=wrong-import-position
# Tell our app about views and model.  This is dangerously close to a
# circular import, which is naughty, but Flask was designed that way.
# (Reference http://flask.pocoo.org/docs/patterns/packages/)  We're
# going to tell pylint and pycodestyle to ignore this coding style violation.
import insta485.views  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.accounts import \
    account_operations  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.accounts import \
    authenticate_account  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.accounts import \
    change_password  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.accounts import \
    create_account  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.accounts import \
    delete_account  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.accounts import \
    edit_account  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.accounts import \
    login_get  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.accounts import \
    logout  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.comments import \
    add_comment  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.explore import \
    show_explore  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.following import \
    update_following  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.index import \
    show_index  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.likes import \
    update_likes  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.posts import \
    show_post  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.posts import \
    update_posts  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.uploads import \
    upload_file  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.users import \
    show_user  # noqa: E402  pylint: disable=wrong-import-position
# from insta485.views.users import \
#     show_user_followers  # noqa: E402  pylint: disable=wrong-import-position
from insta485.views.users import \
    show_user_following  # noqa: E402  pylint: disable=wrong-import-position

# """Views, one for each Insta485 page."""
