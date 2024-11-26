from mutagen.mp3 import MP3
from mutagen.wave import WAVE

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