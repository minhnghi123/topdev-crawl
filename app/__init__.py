from flask import Flask

def create_app():
    # Explicitly set the template folder path
    app = Flask(__name__, template_folder="../templates",static_folder ="../static")
    app.config['SECRET_KEY'] = 'your_secret_key'

    from .routes import main
    app.register_blueprint(main)

    return app