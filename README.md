# Career Explorer AI

A Flask-based web application that helps users explore career opportunities through AI-driven interactions, company visits, and personalized recommendations.

## 🌟 Features

### 1. User Profile & Progression
- Create and manage your professional profile
- Track engagement and progress through levels
- Earn badges for achievements and milestones
- Personalized experience based on interests and goals

### 2. AI-Powered Career Guidance
- Interactive chat with AI career advisor
- Dynamic responses based on user context
- Engaging activities and challenges
- Career-related jokes and trivia
- Progress tracking and insights

### 3. Company Visits & Events
- Personalized company recommendations
- Level-based access to opportunities:
  - Beginners: Start with small startups
  - Advanced: Access to established companies
- Group chats for networking
- Event buddy matching system

### 4. Exclusive Webinars
- Access to webinars at Level 2+
- AI-recommended content
- Interactive sessions
- Networking opportunities

## 🛠 Tech Stack
- Backend: Flask
- AI: Google Gemini API
- Database: SQLAlchemy
- Real-time Chat: Flask-SocketIO
- Frontend: Bootstrap & JavaScript
- Authentication: Flask-Login

## 📋 Requirements
```
flask==2.0.1
flask-socketio==5.1.1
flask-login==0.5.0
flask-sqlalchemy==2.5.1
google-generativeai==0.3.1
python-dotenv==0.19.1
requests==2.31.0
gunicorn==20.1.0
bcrypt==4.0.1
Pillow==10.0.0
python-dateutil==2.8.2
APScheduler==3.10.1
```

## 🚀 Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/career-explorer-ai.git
cd career-explorer-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:
```
FLASK_APP=run.py
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
GEMINI_API_KEY=your-gemini-api-key
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the application:
```bash
python run.py
```

## 🎯 Usage

1. Register an account and complete your profile
2. Start chatting with the AI career advisor
3. Explore recommended companies and events
4. Join webinars and network with other users
5. Track your progress and earn badges

## 🏆 Levels and Progression

1. Level 1: Career Explorer (0 XP)
   - Basic chat access
   - Startup company recommendations

2. Level 2: Professional Seeker (100 XP)
   - Webinar access
   - Enhanced AI interactions

3. Level 3-5: Career Strategist (300-1000 XP)
   - Access to larger companies
   - Advanced networking features

4. Level 6+: Industry Insider (1500+ XP)
   - Enterprise company access
   - Mentorship opportunities

## 🔒 Security

- Passwords are hashed using bcrypt
- API keys are stored securely in environment variables
- User sessions are managed securely
- Input validation and sanitization implemented

## 📱 Mobile Support

The application is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile devices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- Flask and its extensions
- Bootstrap for UI components
- Open source community 