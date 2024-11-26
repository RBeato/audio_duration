from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from pydub import AudioSegment
import os

def get_audio_duration(filepath):
    """
    Get the duration of an audio file in seconds
    """
    file_extension = filepath.lower().split('.')[-1]
    
    if file_extension == 'mp3':
        audio = MP3(filepath)
    elif file_extension == 'wav':
        audio = WAVE(filepath)
    else:
        raise ValueError("Unsupported file format")
        
    return audio.info.length

def trim_audio(input_path, duration_seconds):
    """
    Trim audio file to specified duration in seconds
    Returns: path to trimmed file
    """
    try:
        # Get file extension
        extension = input_path.lower().split('.')[-1]
        
        # Load audio file with explicit format
        if extension == 'mp3':
            audio = AudioSegment.from_mp3(input_path)
        elif extension == 'wav':
            audio = AudioSegment.from_wav(input_path)
        else:
            raise ValueError("Unsupported file format")
        
        # Convert duration to milliseconds
        duration_ms = int(duration_seconds * 1000)
        
        # Trim audio
        trimmed_audio = audio[:duration_ms]
        
        # Generate output filename in the same directory as input
        output_path = os.path.join(
            os.path.dirname(input_path),
            f"trimmed_{os.path.basename(input_path)}"
        )
        
        # Export with specific parameters
        if extension == 'mp3':
            trimmed_audio.export(
                output_path,
                format='mp3',
                bitrate='320k',
                parameters=["-q:a", "0"]  # Use highest quality
            )
        else:  # wav
            trimmed_audio.export(
                output_path,
                format='wav'
            )
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Error trimming audio: {str(e)}") 