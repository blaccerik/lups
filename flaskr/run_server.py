import logging
import os

from flask import Flask, Blueprint
from flask.cli import AppGroup
from flask_cors import CORS
from waitress import serve

# Set the logging level to INFO
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('waitress')
logger.info("log works")



# auth
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # to allow Http traffic for local dev



def init_db():
    from db_models.models import User, Chat, Message, engine, Base, Session
    # Drop all tables
    Base.metadata.drop_all(engine)
    logger.info("dropped")
    # Create all tables
    Base.metadata.create_all(engine)
    logger.info("created")
    # dummy data
    with Session() as session:
        u = User()
        u.name = "erik"
        u.google_id = "2321215345"
        u2 = User()
        u2.name = "erik2"
        u2.google_id = "232323214675475463"
        session.add_all([u, u2])
        session.commit()

        c = Chat()
        c.user_id = u.id
        c2 = Chat()
        c2.user_id = u.id
        c3 = Chat()
        c3.user_id = u2.id
        session.add_all([c, c2, c3])
        session.commit()

        m = Message()
        m.chat_id = c.id
        m.type = "user"
        m.message_ee = "er"
        m.message_en = "3"
        m2 = Message()
        m2.chat_id = c.id
        m2.type = "user"
        m2.message_ee = "er"
        m2.message_en = "3"
        m3 = Message()
        m3.chat_id = c2.id
        m3.type = "bot"
        m3.message_ee = "er"
        m3.message_en = "3"
        session.add_all([m, m2, m3])
        session.commit()


def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = "erik"
    CORS(app)

    logger = logging.getLogger('waitress')
    logger.info("log works")

    # Register API Blueprint and initialize Celery
    from routes import chat, test, auth, news
    api_bp = Blueprint('api', __name__, url_prefix='/api')

    api_bp.register_blueprint(auth.bp)
    api_bp.register_blueprint(chat.bp)
    api_bp.register_blueprint(test.bp)
    api_bp.register_blueprint(news.bp)
    app.register_blueprint(api_bp)

    register_cli_commands(app)  # Register custom CLI commands

    return app


def register_cli_commands(app):
    cli_commands = AppGroup('cli')

    @cli_commands.command('create_tables')
    def create_tables_command():
        with app.app_context():
            init_db()
            logger.info("Tables created")
    app.cli.add_command(cli_commands)


if __name__ == "__main__":
    app = create_app()
    serve(app, host='0.0.0.0', port=5000)
