from app import create_app, socketio
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 5000))
    
    # Run the application with SocketIO
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        allow_unsafe_werkzeug=True  # Only for development
    ) 