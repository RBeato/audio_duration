import os
import logging
from app import create_app

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/var/log/audio_duration.log'
)
logger = logging.getLogger(__name__)

try:
    app = create_app()
    
    if __name__ == "__main__":
        logger.info("Starting Flask application...")
        app.run(host="0.0.0.0", port=5001)
except Exception as e:
    logger.error(f"Failed to start application: {str(e)}", exc_info=True)
    raise 