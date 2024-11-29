import os
import datetime
import json
from app.config import Config

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    now = datetime.datetime.now()
    
    # Check all directories in uploads folder
    for dir_name in os.listdir(Config.UPLOAD_FOLDER):
        dir_path = os.path.join(Config.UPLOAD_FOLDER, dir_name)
        if not os.path.isdir(dir_path):
            continue
            
        # Check metadata file
        metadata_path = os.path.join(dir_path, 'metadata.json')
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                created_at = datetime.datetime.fromisoformat(metadata['created_at'])
                
                # If older than 1 hour, delete everything
                if (now - created_at).total_seconds() > 3600:
                    for file in os.listdir(dir_path):
                        os.remove(os.path.join(dir_path, file))
                    os.rmdir(dir_path)
            except Exception as e:
                print(f"Error cleaning up {dir_path}: {str(e)}") 