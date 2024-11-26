import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.audio_processor import get_audio_duration
from app.config import Config

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3', 'wav'}

def cleanup_file(filepath):
    """Helper function to safely delete a file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error cleaning up file {filepath}: {str(e)}")

@main.route('/get_duration', methods=['POST'])
def process_audio():
    filepath = None
    try:
        # Check API key
        api_key = request.headers.get('X-API-KEY')
        print(f"Received API key: {api_key}")
        print(f"Expected API key: {Config.API_KEY}")
        
        if api_key != Config.API_KEY:
            return jsonify({
                'error': 'Invalid API key',
                'received': api_key,
                'expected': Config.API_KEY
            }), 401

        # Check if file was uploaded
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only MP3 and WAV files are allowed'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # Ensure upload directory exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Save file temporarily
        file.save(filepath)
        
        # Get duration
        duration = get_audio_duration(filepath)
        
        # Prepare response
        response = {
            'duration': duration,
            'filename': filename
        }
        
        # Clean up file
        cleanup_file(filepath)
        
        return jsonify(response)
    
    except Exception as e:
        # Ensure cleanup happens even if there's an error
        if filepath:
            cleanup_file(filepath)
        return jsonify({'error': str(e)}), 500