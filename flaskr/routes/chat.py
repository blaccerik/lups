from flask import Blueprint, jsonify, request

from routes.test import token_required
from schemas.schemas import ChatResponseSchema
from services.chat_service import *

bp = Blueprint('chat', __name__, url_prefix="/chat")
response_schema = ChatResponseSchema()



@bp.route("/create", methods=['POST'])
@token_required
def create(google_id, name):
    return jsonify(), 200

@bp.route("", methods=['GET'])
@token_required
def chats(google_id, name):
    user_id = get_user(name, google_id)
    chats = get_chats(user_id)
    return jsonify(chats), 200

@bp.route("/<int:chat_id>", methods=['GET'])
@token_required
def chat_get(chat_id, google_id, name):
    user_id = get_user(name, google_id)
    msgs = get_chat(user_id, chat_id)
    return jsonify(msgs), 200


@bp.route("/<int:chat_id>", methods=['DELETE'])
@token_required
def chat_delete(chat_id, google_id, name):
    user_id = get_user(name, google_id)
    clear(user_id, chat_id)
    return jsonify("deleted"), 200


@bp.route("/<int:chat_id>", methods=['POST'])
@token_required
def chat_post(chat_id, google_id, name):
    user_id = get_user(name, google_id)
    text = request.json["text"]
    response = post_message(user_id, chat_id, text)
    return jsonify(response), 200