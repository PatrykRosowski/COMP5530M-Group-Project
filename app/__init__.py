from flask import Flask
from flask_cors import CORS
from app.utils.settings import Config

def create_app(config_class=Config):
    print("create_app: Starting function")
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)
    print("create_app: CORS initialized")
    from app.api import api_bp
    print("create_app: Before registering api_bp")
    app.register_blueprint(api_bp, url_prefix="/api")
    print("create_app: After registering api_bp")
    print("create_app: Returning app")
    return app