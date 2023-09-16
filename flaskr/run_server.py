import logging
import os

from flask import Flask, Blueprint
from flask.cli import AppGroup
from flask_cors import CORS

from db_models.models import init_db, populate_db
from routes.place import socketio
from shared import logger

# auth
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # to allow Http traffic for local dev


def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = "erik"
    CORS(app)

    logger2 = logging.getLogger('waitress')
    logger2.info("log works")

    # Register API Blueprint and initialize Celery
    from routes import chat, test, auth, news
    api_bp = Blueprint('api', __name__, url_prefix='/api')

    api_bp.register_blueprint(auth.bp)
    api_bp.register_blueprint(chat.bp)
    api_bp.register_blueprint(test.bp)
    api_bp.register_blueprint(news.bp)
    app.register_blueprint(api_bp)

    socketio.init_app(app)

    register_cli_commands(app)  # Register custom CLI commands

    return app


def register_cli_commands(app):
    cli_commands = AppGroup('cli')
    # todo clear images if new database
    @cli_commands.command('create_tables')
    def create_tables_command():
        with app.app_context():
            init_db()
            logger.info("Tables created")

    @cli_commands.command('populate_tables')
    def populate_tables_command():
        with app.app_context():
            init_db()
            populate_db()
            logger.info("Tables populated")

    app.cli.add_command(cli_commands)


app = create_app()

if __name__ == "__main__":
    logger.info("HEREEEEE")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    # serve(app, host='0.0.0.0', port=5000)
