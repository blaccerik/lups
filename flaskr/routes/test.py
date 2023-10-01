import io
from functools import wraps

from flask import Blueprint, request, jsonify, send_file
from google.auth.transport import requests
from google.oauth2 import id_token

from shared import logger

bp = Blueprint('test', __name__, url_prefix="/test")

YOUR_CLIENT_ID = '437646142767-evt2pt3tn4pbrjcea6pd71quq07h82j7.apps.googleusercontent.com'


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if not access_token:
            logger.info("no token")
            return jsonify({'message': 'Missing access token'}), 401
        access_token = access_token.split(" ")[1]
        try:
            id_info = id_token.verify_oauth2_token(access_token, requests.Request(), YOUR_CLIENT_ID)
            google_id = id_info.get('sub')
            name = id_info.get("name")
            logger.info(f"{google_id} {name}")
            kwargs['google_id'] = google_id
            kwargs['name'] = name
            return f(*args, **kwargs)
        except ValueError as e:
            logger.info(e)
            return jsonify({'error': str(e)}), 401

    return decorated_function


@bp.route('', methods=['GET'])
def get():
    return jsonify("get works"), 200


@bp.route('/<int:chat_id>', methods=['GET'])
def get_id(chat_id):
    return jsonify(f"get id works {chat_id}"), 200


@bp.route("/query", methods=["GET"])
def get_query():
    page = int(request.args.get('page'))
    return jsonify(f"get query works {page}"), 200


@bp.route('', methods=['POST'])
def post():
    data = request.json
    text = data["text"]
    return jsonify(f"post works {text}"), 200


@bp.route('/form', methods=['GET'])
def get_form():
    # Create a Blob (in this example, a simple text Blob)
    text = "Blob from server"
    blob = io.BytesIO(text.encode('utf-8'))
    return send_file(blob, mimetype='text/plain')


@bp.route('/form', methods=['POST'])
def post_form():
    data = request.form
    t = data.get("test")
    t2 = request.files.get("file")
    blob_text = t2.read().decode('utf-8')
    return jsonify(f"blob: {blob_text} text: {t}"), 200


@bp.route('/protected', methods=['GET'])
@token_required
def get_protected(google_id, name):
    return jsonify(f"get protected works {name}"), 200


@bp.route('/protected/<int:chat_id>', methods=['GET'])
@token_required
def get_id_protected(chat_id, google_id, name):
    return jsonify(f"get protected id works {chat_id} {name}"), 200


@bp.route('/protected', methods=['POST'])
@token_required
def post_protected(google_id, name):
    data = request.json
    text = data["text"]
    return jsonify(f"post protected works {text} {name}"), 200
