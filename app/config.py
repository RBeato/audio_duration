import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    API_KEY = os.environ.get('API_KEY')
    UPLOAD_FOLDER = '/opt/audio_duration/app/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 