import google.auth.transport.requests
import requests
from flask import session, abort, redirect, request, Blueprint, jsonify
from google.oauth2 import id_token
from pip._vendor import cachecontrol

from run_server import flow, GOOGLE_CLIENT_ID

bp = Blueprint('auth', __name__, url_prefix="/auth")

database = {}  # Global dictionary to store user data

@bp.route('/login')
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@bp.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")

    # # Add user to the database if not already present
    # if session["google_id"] not in database:
    #     database[session["google_id"]] = {
    #         "google_id": session["google_id"],
    #         "name": session["name"]
    #     }

    return redirect("/api/auth/protected_area")

@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/api/auth")

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session: # or session["google_id"] not in database:
            return abort(401)  # Authorization required
        else:
            return function(*args, **kwargs)

    return wrapper

@bp.route("/")
def index():
    return "Hello World <a href='/api/auth/login'><button>Login</button></a>"

@bp.route("/protected_area")
@login_is_required
def protected_area():
    return f"Hello {session['name']}! <br/> <a href='/api/auth/logout'><button>Logout</button></a>"
