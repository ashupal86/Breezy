from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# Association tables
user_badges = db.Table('user_badges',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('badge_id', db.Integer, db.ForeignKey('badge.id'))
)

event_participants = db.Table('event_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

group_chat_members = db.Table('group_chat_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('chat_id', db.Integer, db.ForeignKey('group_chat.id'))
)

user_connections = db.Table('user_connections',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('connected_user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    linkedin_profile = db.Column(db.String(255), nullable=True)
    interests = db.Column(db.String(500), nullable=True)
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_company_admin = db.Column(db.Boolean, default=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    badges = db.relationship('Badge', secondary='user_badges', backref='users')
    registered_events = db.relationship('Event', secondary='event_participants', backref='participants')
    connections = db.relationship(
        'User', secondary='user_connections',
        primaryjoin='User.id==user_connections.c.user_id',
        secondaryjoin='User.id==user_connections.c.connected_user_id',
        backref='connected_by'
    )
    chat_messages = db.relationship('ChatMessage', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self):
        """Generate a password reset token"""
        token = secrets.token_urlsafe(32)
        self.reset_token = token
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        return token

    def verify_reset_token(self, token):
        """Verify if reset token is valid"""
        if self.reset_token != token:
            return False
        if not self.reset_token_expiry or self.reset_token_expiry < datetime.utcnow():
            return False
        return True
    
    def add_experience(self, points):
        """Add experience points and update level"""
        self.experience += points
        self.level = self.calculate_level()
        return self.level
    
    def calculate_level(self):
        """Calculate user level based on experience points"""
        from app.utils.progress_tracker import ProgressTracker
        return ProgressTracker.calculate_level(self.experience)
    
    def can_attend_webinars(self):
        """Check if user can attend webinars (Level 2+)"""
        return self.level >= 2
    
    def get_recommended_company_type(self):
        """Get recommended company type based on user level"""
        if self.level <= 2:
            return 'startup'
        elif self.level <= 5:
            return 'medium'
        else:
            return 'enterprise'
    
    def has_badge(self, badge_name):
        """Check if user has a specific badge"""
        return any(badge.name == badge_name for badge in self.badges)

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    industry = db.Column(db.String(100))
    size = db.Column(db.String(20))  # 'startup', 'medium', 'enterprise'
    logo = db.Column(db.String(200))
    events = db.relationship('Event', backref='company', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)  # in minutes
    max_participants = db.Column(db.Integer)
    level_required = db.Column(db.Integer, default=1)
    points = db.Column(db.Integer, default=50)  # XP points for attending
    event_type = db.Column(db.String(20))  # 'company_visit' or 'webinar'
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    group_chat_id = db.Column(db.Integer, db.ForeignKey('group_chat.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GroupChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, unique=True)
    messages = db.relationship('ChatMessage', backref='group_chat', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_chat_id = db.Column(db.Integer, db.ForeignKey('group_chat.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    sentiment_score = db.Column(db.Float)
    engagement_score = db.Column(db.Float)
    topics = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) 