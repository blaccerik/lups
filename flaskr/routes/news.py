import os

from PIL import Image
from flask import Blueprint, request, jsonify, send_file

from routes.test import token_required
from services.chat_service import get_user
from services.news_service import create_news, save_file, get_news, find_image, edit

bp = Blueprint('news', __name__, url_prefix="/news")


@bp.route("/create", methods=['POST'])
@token_required
def create(google_id, name):
    user_id = get_user(name, google_id)
    title = request.form.get('title')
    text = request.form.get('text')
    file = request.files.get('file')
    news_id = create_news(user_id, title, text)
    if file:
        save_file(file, news_id)
    return jsonify(news_id), 200

@bp.route("/<int:news_id>", methods=['PUT'])
@token_required
def edit_news(news_id, google_id, name):
    user_id = get_user(name, google_id)

    title = request.form.get('title')
    text = request.form.get('text')
    new_file = request.form.get("new_file")
    file = request.files.get('file')


    print(new_file)
    print(file)
    # check if can edit
    edit(news_id, user_id, title, text, new_file, file)
    return jsonify(f"Edited {news_id}"), 200


@bp.route("/<int:news_id>", methods=['GET'])
def chat_get(news_id):
    news = get_news(news_id)
    return jsonify(news), 200


@bp.route("/<int:news_id>/image", methods=['GET'])
def get_image(news_id):
    path = find_image(news_id)
    return send_file(path, mimetype="image/jpeg")
