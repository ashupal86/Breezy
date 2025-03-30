from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import google.generativeai as genai
from config import Config

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO()

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure app
    app.config.from_object(config_class)
    
    # Configure Gemini API
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    socketio.init_app(app)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Register blueprints
    from app.routes.main import main
    app.register_blueprint(main)

    from app.routes.auth import auth
    app.register_blueprint(auth)

    from app.routes.events import events_bp
    app.register_blueprint(events_bp)

    from app.routes.chat import chat
    app.register_blueprint(chat)
    
    @login_manager.user_loader
    def load_user(id):
        from app.models.models import User
        return User.query.get(int(id))
    
    return app 