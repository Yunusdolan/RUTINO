
import os
from flask import Flask
from database import db
from configure_security import configure_security


def create_app():
    app = Flask(__name__)

    configure_security(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from models import Kullanici, Aliskanlik, Sikayet, HabitRecord
    from routes import routes

    app.register_blueprint(routes)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=app.config["DEBUG"]
    )
