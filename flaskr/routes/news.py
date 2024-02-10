import os

from PIL import Image
from flask import Blueprint, request, jsonify, send_file

from routes.test import token_required
from services.chat_service import read_user
from services.news_service import add_news, save_file, get_news, find_image, get_news_many

bp = Blueprint('news', __name__, url_prefix="/news")


@bp.route("/create", methods=['POST'])
@token_required
def create(google_id, name):
    user_id = read_user(name, google_id)
    title = request.form.get('title')
    text = request.form.get('text')
    file = request.files.get('file')
    cat = request.form.get("category")

    news_id = add_news(user_id, title, text, cat, file)
    return jsonify(news_id), 200


@bp.route("/<int:news_id>", methods=['PUT'])
@token_required
def edit_news(news_id, google_id, name):

    user_id = read_user(name, google_id)
    title = request.form.get('title')
    text = request.form.get('text')
    cat = request.form.get("category")
    file = request.files.get('file')

    news_id = add_news(user_id, title, text, cat, file, news_id)
    return jsonify(news_id), 200


@bp.route("/", methods=['GET'])
def news_get():
    try:
        page_number = int(request.args.get('page', default=0))
    except:
        page_number = 0
    news = get_news_many(page_number)
    return jsonify(news)


@bp.route("/<int:news_id>", methods=['GET'])
def news_get_single(news_id):
    news = get_news(news_id)
    return jsonify(news), 200


@bp.route("/<int:news_id>/image", methods=['GET'])
def get_image(news_id):
    path = find_image(news_id)
    return send_file(path, mimetype="image/jpeg")
