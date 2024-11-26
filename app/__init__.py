from flask import Flask
from app.config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Ensure upload directory exists with proper permissions
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.chmod(app.config['UPLOAD_FOLDER'], 0o777)
    
    from app.routes import main
    app.register_blueprint(main)
    
    return app 