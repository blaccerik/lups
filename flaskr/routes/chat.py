from flask import Blueprint, jsonify, request, Response
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
    logger.info(user_id)
    text = request.json["text"]
    response = post_message(user_id, chat_id, text)
    return jsonify(response), 200


@bp.route('/stream')
# @token_required
def stream_text():
    def test():
        sections = ['Section 1', 'Section 2', 'Section 3', 'Section 4']
        for section in sections:
            time.sleep(1)
            yield section

    return Response(test(), mimetype='text/stream')


# celery2 = Celery("tasks")
# celery2.conf.broker_url = "redis://localhost:6379/0"
# celery2.conf.result_backend = 'redis://localhost:6379/0'


# cel = Celery('myapp', broker='amqp://localhost:5672', backend='rpc://')
#
#
# @bp.route('/start')
# def start_task():
#     task = cel.send_task("hello")
#     print(task)
#     a = task.get()
#     print(a)
#     # a = task.get(on_message=on_raw_message, propagate=False)
#     # print(a)
#     return "23"
#
# stream_clients = []
# def sse_stream():
#     for client in stream_clients:
#         print(client)
#         yield f"data: {client['section']}\n\n"
#
# def on_raw_message(body):
#     # Add the message to the stream_clients list
#     stream_clients.append({'section': body})
# @bp.route("/start2")
# def start_task2():
#     r = cel.send_task("hello2")
#     # Start streaming to the client by sending an initial response
#     initial_response = "Starting stream"
#     for client in stream_clients:
#         client['section'] = initial_response
#
#     a = r.get(on_message=on_raw_message, propagate=False)
#     return "done"
#
# @bp.route('/stream2')
# def stream_data():
#     return Response(sse_stream(), mimetype='text/event-stream')

