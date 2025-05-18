from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import db
import os

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder ="../static")
    app.config['SECRET_KEY'] = 'your_secret_key'
    # Use absolute path for SQLite DB
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, 'Data', 'crawl.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app