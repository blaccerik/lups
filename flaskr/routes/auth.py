from flask import Blueprint, jsonify
from flask import request
from google.auth.transport import requests
from google.oauth2 import id_token
from run_server import logger

bp = Blueprint('auth', __name__, url_prefix="/auth")

YOUR_CLIENT_ID = '437646142767-evt2pt3tn4pbrjcea6pd71quq07h82j7.apps.googleusercontent.com'
@bp.route('/test')
def protected():
    a = request.headers.get("sub")
    print(a)
    return f"Hi, {3}! This is a protected route."

@bp.route("/login", methods=['POST'])
def login():
    access_token = request.json.get('access_token')
    print(access_token)
    # Verify the access token against Google's token endpoint
    try:
        id_info = id_token.verify_oauth2_token(access_token, requests.Request(), YOUR_CLIENT_ID)
        user_id = id_info.get('sub')
        email = id_info.get('email')

        # Return a success response
        return jsonify({'message': 'Access token is valid', 'user_id': user_id, 'email': email}), 200
    except ValueError as e:
        logger.info(e)
        return jsonify({'error': str(e)}), 401
#
# @bp.route("/callback")
# def callback():
#     token = flow.fetch_token(authorization_response=request.url)
#     if not session["state"] == request.args["state"]:
#         abort(500)  # State does not match!
#
#     request_session = requests.session()
#     cached_session = cachecontrol.CacheControl(request_session)
#     token_request = google.auth.transport.requests.Request(session=cached_session)
#
#     # Validate the access token
#     id_info = id_token.verify_oauth2_token(
#         id_token=token["id_token"],
#         request=token_request,
#     )
#     # Retrieve user information
#     google_id = id_info.get("sub")
#     name = id_info.get("name")
#
#     # gen jwt token
#     print(google_id, name)
#     return "jwt_token", 200


#
# @bp.route('/login', methods=['POST'])
# def login():
#     google_session_data = request.get_json()  # Assuming the Google session data is sent as JSON in the request body
#
#     # Verify the authenticity and integrity of the Google session data
#     try:
#         id_token.verify_oauth2_token(
#             google_session_data["id_token"], requests.Request()
#         )
#     except ValueError:
#         return {"message": "Invalid Google session data"}, 401
#     return "eee", 200


# @bp.route("/callback")
# def callback():
#     token = flow.fetch_token(authorization_response=request.url)
#     if not session["state"] == request.args["state"]:
#         abort(500)  # State does not match!
#
#     request_session = requests.session()
#     cached_session = cachecontrol.CacheControl(request_session)
#     token_request = google.auth.transport.requests.Request(session=cached_session)
#
#     # Validate the access token
#     id_info = id_token.verify_oauth2_token(
#         id_token=token["id_token"],
#         request=token_request,
#     )
#     # Retrieve user information
#     google_id = id_info.get("sub")
#     name = id_info.get("name")
#
#     # Generate JWT token
#     jwt_payload = {
#         "sub": google_id,
#         "name": name,
#         "exp": datetime.utcnow() + timedelta(days=1)  # Token expiration time (e.g., 1 day)
#     }
#     jwt_token = jwt.encode(jwt_payload, current_app.secret_key, algorithm="HS256")
#
#     # gen jwt token
#     return jwt_token, 200
#
#
# def jwt_required(func):
#     @wraps(func)
#     def decorated(*args, **kwargs):
#         # Check if Authorization header is present
#         auth_header = request.headers.get("Authorization")
#         if not auth_header or not auth_header.startswith("Bearer "):
#             return "Unauthorized", 401
#
#         # Extract and verify the JWT token
#         jwt_token = auth_header.split(" ")[1]
#         secret_key = current_app.secret_key
#         try:
#             decoded_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
#             # Retrieve the name from the decoded token
#             name = decoded_token.get("name")
#             if name:
#                 # Call the protected route handler function and pass the name
#                 return func(name, *args, **kwargs)
#             else:
#                 return "Unauthorized", 401
#         except jwt.ExpiredSignatureError:
#             return "Token has expired", 401
#         except (jwt.InvalidTokenError, jwt.exceptions.DecodeError):
#             return "Invalid token", 401
#
#     return decorated
#
#
# @bp.route('/test')
# @jwt_required
# def protected(name):
#     return f"Hi, {name}! This is a protected route."
#
# #
# @bp.route("/callback")
# def callback():
#     flow.fetch_token(authorization_response=request.url)
#     if not session["state"] == request.args["state"]:
#         abort(500)  # State does not match!
#     credentials = flow.credentials
#     request_session = requests.session()
#     cached_session = cachecontrol.CacheControl(request_session)
#     token_request = google.auth.transport.requests.Request(session=cached_session)
#
#     id_info = id_token.verify_oauth2_token(
#         id_token=credentials._id_token,
#         request=token_request,
#         audience=GOOGLE_CLIENT_ID
#     )
#     session["google_id"] = id_info.get("sub")
#     session["name"] = id_info.get("name")
#
#     # Add user to the database if not already present
#     user = db_session.query(User).filter_by(google_id=session["google_id"]).first()
#     if user is None:
#         u = User()
#         u.name = session["name"]
#         u.google_id = session["google_id"]
#         db_session.add(u)
#         db_session.commit()
#
#     return redirect(FRONTEND_BASE_URL)
#
# @bp.route("/logout")
# def logout():
#     session.clear()
#     return redirect("/api/auth")
#
# def login_is_required(function):
#     def wrapper(*args, **kwargs):
#         if "google_id" not in session: # or session["google_id"] not in database:
#             return abort(401)  # Authorization required
#         else:
#             return function(*args, **kwargs)
#
#     return wrapper
#
# @bp.route("/")
# def index():
#     return "Hello World <a href='/api/auth/login'><button>Login</button></a>"
#
# @bp.route("/protected_area")
# @login_is_required
# def protected_area():
#     return f"Hello {session['name']}! <br/> <a href='/api/auth/logout'><button>Logout</button></a>"
