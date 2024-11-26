from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from pydub import AudioSegment

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
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        
        # Convert duration to milliseconds
        duration_ms = duration_seconds * 1000
        
        # Trim audio
        trimmed_audio = audio[:duration_ms]
        
        # Generate output filename
        filename = input_path.rsplit('.', 1)[0]
        extension = input_path.rsplit('.', 1)[1]
        output_path = f"{filename}_trimmed.{extension}"
        
        # Export trimmed audio
        trimmed_audio.export(output_path, format=extension)
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Error trimming audio: {str(e)}") 