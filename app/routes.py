import os
from flask import Blueprint, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
from app.audio_processor import get_audio_duration, trim_audio
from app.config import Config
import logging
import uuid

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

# Store temporary files with their IDs
TEMP_FILES = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3', 'wav'}

def cleanup_file(filepath):
    """Helper function to safely delete a file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        logger.error(f"Error cleaning up file {filepath}: {str(e)}")

@main.route('/trim_audio', methods=['POST'])
def trim_audio_endpoint():
    filepath = None
    trimmed_filepath = None
    try:
        # Check API key
        api_key = request.headers.get('X-API-KEY')
        if api_key != Config.API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401

        # Get duration parameter
        duration = request.form.get('duration')
        if not duration:
            return jsonify({'error': 'Duration parameter is required'}), 400
        
        try:
            duration = float(duration)
        except ValueError:
            return jsonify({'error': 'Duration must be a number'}), 400

        # Check if file was uploaded
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only MP3 and WAV files are allowed'}), 400

        # Generate unique ID for this file
        file_id = str(uuid.uuid4())
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        logger.debug(f"Saving file to: {filepath}")
        
        # Ensure upload directory exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Save file temporarily
        file.save(filepath)
        logger.debug(f"File saved, size: {os.path.getsize(filepath)}")
        
        # Trim audio
        trimmed_filepath = trim_audio(filepath, duration)
        logger.debug(f"Trimmed file created at: {trimmed_filepath}")
        logger.debug(f"Trimmed file size: {os.path.getsize(trimmed_filepath)}")
        
        # Store the trimmed file path with its ID
        TEMP_FILES[file_id] = {
            'path': trimmed_filepath,
            'original': filepath
        }
        
        # Generate download URL
        download_url = f"http://164.90.165.124:5001/download/{file_id}"
        
        # Return the download link
        return jsonify({
            'message': 'Audio trimmed successfully',
            'download_url': download_url,
            'file_id': file_id
        })
        
    except Exception as e:
        logger.error(f"Error in trim_audio_endpoint: {str(e)}", exc_info=True)
        # Ensure cleanup happens if there's an error
        if filepath:
            cleanup_file(filepath)
        if trimmed_filepath:
            cleanup_file(trimmed_filepath)
        return jsonify({'error': str(e)}), 500

@main.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    try:
        if file_id not in TEMP_FILES:
            return jsonify({'error': 'File not found'}), 404
            
        file_info = TEMP_FILES[file_id]
        trimmed_filepath = file_info['path']
        
        if not os.path.exists(trimmed_filepath):
            return jsonify({'error': 'File no longer exists'}), 404
            
        response = send_file(
            trimmed_filepath,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=os.path.basename(trimmed_filepath)
        )
        
        # Clean up after sending
        @response.call_on_close
        def cleanup():
            logger.debug("Cleaning up files...")
            cleanup_file(file_info['original'])
            cleanup_file(file_info['path'])
            TEMP_FILES.pop(file_id, None)
            
        return response
        
    except Exception as e:
        logger.error(f"Error in download_file: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

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