import logging
import os

from flask import Flask, Blueprint
from flask.cli import AppGroup
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from waitress import serve



# Set the logging level to INFO
logging.basicConfig(level=logging.INFO)

uri = f"mysql+pymysql://" \
      f"{os.environ.get('MYSQL_USER', 'erik')}:" \
      f"{os.environ.get('MYSQL_PASSWORD', 'erik')}@localhost:3306/" \
      f"{os.environ.get('MYSQL_DATABASE', 'erik_db')}"

engine = create_engine(uri)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from db_models.models import User

    # Drop all tables
    Base.metadata.drop_all(bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    u = User()
    u.name = "erik"
    u.n = "ewewe"
    db_session.add(u)
    db_session.commit()

def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    logger = logging.getLogger('waitress')
    logger.info("log works")

    # Register API Blueprint and initialize Celery
    from routes import chat, test
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    api_bp.register_blueprint(chat.bp)
    api_bp.register_blueprint(test.bp)
    app.register_blueprint(api_bp)

    register_cli_commands(app)  # Register custom CLI commands

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        print("end")
        db_session.remove()

    return app


def register_cli_commands(app):
    cli_commands = AppGroup('cli')

    @cli_commands.command('create_tables')
    def create_tables_command():
        with app.app_context():
            init_db()
            print('Tables created successfully!')

    app.cli.add_command(cli_commands)




if __name__ == "__main__":
    app = create_app()
    serve(app, host='0.0.0.0', port=5000)
