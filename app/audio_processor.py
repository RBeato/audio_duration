from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from pydub import AudioSegment
import os
import logging

logger = logging.getLogger(__name__)

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
        logger.debug(f"Starting trim_audio with input: {input_path}, duration: {duration_seconds}")
        
        # Check if input file exists and is readable
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file does not exist: {input_path}")
        
        logger.debug(f"Input file exists and size is: {os.path.getsize(input_path)} bytes")
        logger.debug(f"Input file permissions: {oct(os.stat(input_path).st_mode)[-3:]}")
        
        # Check if output directory is writable
        output_dir = os.path.dirname(input_path)
        if not os.access(output_dir, os.W_OK):
            raise PermissionError(f"Output directory is not writable: {output_dir}")
        
        # Get file extension
        extension = input_path.lower().split('.')[-1]
        logger.debug(f"File extension: {extension}")
        
        # Load audio file with explicit format
        if extension == 'mp3':
            logger.debug("Loading MP3 file...")
            audio = AudioSegment.from_mp3(input_path)
        elif extension == 'wav':
            logger.debug("Loading WAV file...")
            audio = AudioSegment.from_wav(input_path)
        else:
            raise ValueError("Unsupported file format")
        
        logger.debug(f"Audio loaded, duration: {len(audio)}ms")
        
        # Convert duration to milliseconds
        duration_ms = int(duration_seconds * 1000)
        logger.debug(f"Target duration: {duration_ms}ms")
        
        # Trim audio
        trimmed_audio = audio[:duration_ms]
        logger.debug(f"Audio trimmed, new duration: {len(trimmed_audio)}ms")
        
        # Generate output filename in the same directory as input
        output_path = os.path.join(
            os.path.dirname(input_path),
            f"trimmed_{os.path.basename(input_path)}"
        )
        logger.debug(f"Output path: {output_path}")
        
        # Export with specific parameters
        if extension == 'mp3':
            logger.debug("Exporting as MP3...")
            trimmed_audio.export(
                output_path,
                format='mp3',
                bitrate='320k',
                codec="libmp3lame",
                parameters=["-q:a", "0"]  # Use highest quality
            )
        else:  # wav
            logger.debug("Exporting as WAV...")
            trimmed_audio.export(
                output_path,
                format='wav'
            )
        
        logger.debug(f"Export complete. File size: {os.path.getsize(output_path)}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error in trim_audio: {str(e)}", exc_info=True)
        raise Exception(f"Error trimming audio: {str(e)}") 