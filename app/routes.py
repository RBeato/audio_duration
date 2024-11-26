import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from app.audio_processor import get_audio_duration, trim_audio
from app.config import Config
import logging
import uuid
import datetime
import time
import threading
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3', 'wav'}

def cleanup_file(filepath):
    """Helper function to safely delete a file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.debug(f"Cleaned up file: {filepath}")
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
        
        # Create a directory for this specific request
        request_dir = os.path.join(Config.UPLOAD_FOLDER, file_id)
        os.makedirs(request_dir, exist_ok=True)
        
        # Add debug logging
        logger.debug(f"Request directory created at: {request_dir}")
        logger.debug(f"File permissions on request_dir: {oct(os.stat(request_dir).st_mode)[-3:]}")
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(request_dir, filename)
        logger.debug(f"Saving file to: {filepath}")
        
        # Save file temporarily
        file.save(filepath)
        logger.debug(f"File saved successfully, checking existence: {os.path.exists(filepath)}")
        logger.debug(f"File permissions: {oct(os.stat(filepath).st_mode)[-3:]}")
        
        # Trim audio
        logger.debug(f"Attempting to trim audio file: {filepath}")
        trimmed_filepath = trim_audio(filepath, duration)
        logger.debug(f"Trim operation completed, checking trimmed file: {trimmed_filepath}")
        logger.debug(f"Trimmed file exists: {os.path.exists(trimmed_filepath)}")
        
        # Create a metadata file
        metadata = {
            'path': trimmed_filepath,
            'original': filepath,
            'created_at': str(datetime.datetime.now())
        }
        
        metadata_path = os.path.join(request_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        # Generate download URL
        download_url = f"http://164.90.165.124:5001/download/{file_id}"
        
        return jsonify({
            'message': 'Audio trimmed successfully',
            'download_url': download_url,
            'file_id': file_id
        })
        
    except Exception as e:
        logger.error(f"Error in trim_audio_endpoint: {str(e)}", exc_info=True)
        if filepath:
            cleanup_file(filepath)
        if trimmed_filepath:
            cleanup_file(trimmed_filepath)
        return jsonify({'error': str(e)}), 500

@main.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    try:
        logger.debug(f"Download requested for file_id: {file_id}")
        
        # Check if the directory exists
        request_dir = os.path.join(Config.UPLOAD_FOLDER, file_id)
        metadata_path = os.path.join(request_dir, 'metadata.json')
        
        if not os.path.exists(metadata_path):
            logger.error(f"Metadata file not found for ID: {file_id}")
            return jsonify({'error': 'File not found'}), 404
            
        # Load metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            
        trimmed_filepath = metadata['path']
        logger.debug(f"Attempting to send file: {trimmed_filepath}")
        
        if not os.path.exists(trimmed_filepath):
            logger.error(f"File does not exist at path: {trimmed_filepath}")
            return jsonify({'error': 'File no longer exists'}), 404
            
        response = send_file(
            trimmed_filepath,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=os.path.basename(trimmed_filepath)
        )
        
        @response.call_on_close
        def cleanup_after_send():
            logger.debug("Starting cleanup after file send")
            cleanup_file(metadata['original'])
            cleanup_file(metadata['path'])
            cleanup_file(metadata_path)
            try:
                os.rmdir(request_dir)
                logger.debug(f"Cleaned up directory: {request_dir}")
            except Exception as e:
                logger.error(f"Error removing directory: {str(e)}")
            
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