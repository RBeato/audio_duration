from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from pydub import AudioSegment
import os

def get_audio_duration(filepath):
    """Get the duration of an audio file in seconds"""
    file_extension = filepath.lower().split('.')[-1]
    
    if file_extension == 'mp3':
        audio = MP3(filepath)
    elif file_extension == 'wav':
        audio = WAVE(filepath)
    else:
        raise ValueError("Unsupported file format")
        
    return audio.info.length

def trim_audio(input_path, duration_seconds):
    """Trim audio file to specified duration in seconds"""
    try:
        # Get file extension
        extension = input_path.lower().split('.')[-1]
        
        # Load audio file
        if extension == 'mp3':
            audio = AudioSegment.from_mp3(input_path)
        elif extension == 'wav':
            audio = AudioSegment.from_wav(input_path)
        else:
            raise ValueError("Unsupported file format")
        
        # Convert duration to milliseconds and trim
        duration_ms = int(duration_seconds * 1000)
        trimmed_audio = audio[:duration_ms]
        
        # Generate output filename
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
                codec="libmp3lame",
                parameters=["-q:a", "0"]
            )
        else:  # wav
            trimmed_audio.export(
                output_path,
                format='wav'
            )
        
        return output_path
        
    except Exception as e:
        print(f"Error trimming audio: {str(e)}")
        raise

def test_audio_functions(audio_path, trim_duration=None):
    """Test audio processing functions"""
    try:
        # Test get_duration
        print("\n=== Testing get_duration ===")
        duration = get_audio_duration(audio_path)
        print(f"Audio duration: {duration} seconds")

        # Test trim_audio if duration is provided
        if trim_duration:
            print(f"\n=== Testing trim_audio (trimming to {trim_duration} seconds) ===")
            trimmed_path = trim_audio(audio_path, trim_duration)
            print(f"Trimmed file created at: {trimmed_path}")
            
            # Verify trimmed duration
            trimmed_duration = get_audio_duration(trimmed_path)
            print(f"Trimmed file duration: {trimmed_duration} seconds")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Replace this with the path to your MP3 file
    audio_file = "C:/Users/rbsou/Documents/CODE/py_video_creator/input/music.mp3"
    
    # Test both functions (get duration and trim to 30 seconds)
    test_audio_functions(audio_file, trim_duration=30) 