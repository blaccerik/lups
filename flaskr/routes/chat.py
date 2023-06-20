import os
import logging

from celery import Celery
from flask import Blueprint, jsonify, request

from schemas.schemas import ChatResponseSchema

bp = Blueprint('chat', __name__, url_prefix="/chat")
response_schema = ChatResponseSchema()


celery = Celery("tasks")
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@bp.route('', methods=['POST'])
def test():
    data = request.json
    input_text = data['text']
    logger = logging.getLogger('waitress')
    logger.info(input_text)
    task = celery.send_task("tasks.create_task", args=[input_text])
    logger.info(task)
    try:
        output_text_ee, output_text_en = task.get()
    except Exception as e:
        logger.exception(e)
        return jsonify({"message": "server busy"}), 408
    return jsonify({
        "output_text_en": output_text_en,
        "output_text_ee": output_text_ee
    }), 200

@bp.route('', methods=['GET'])
def test2():

    logger = logging.getLogger('waitress')
    logger.info('Hello baby!')
    task = celery.send_task("tasks.create_task", args=["tere"])
    logger.info(task)
    try:
        output_text_ee, output_text_en = task.get()
    except Exception as e:
        logger.exception(e)
        return jsonify({"message": "server busy"}), 408
    return jsonify({
        "output_text_en": output_text_en,
        "output_text_ee": output_text_ee
    }), 200
