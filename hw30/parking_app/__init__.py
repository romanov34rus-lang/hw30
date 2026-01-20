from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)

    if testing:
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
    else:
        app.config.update(
            SQLALCHEMY_DATABASE_URI="sqlite:///parking.db",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )

    db.init_app(app)

    from .routes import api

    app.register_blueprint(api)

    return app

