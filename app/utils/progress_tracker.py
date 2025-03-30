from app.models.models import User, Badge, Event
from app import db
from datetime import datetime, timedelta
import math

class ProgressTracker:
    # Experience points required for each level
    LEVEL_THRESHOLDS = {
        1: 0,      # Starting level
        2: 100,    # Basic engagement
        3: 300,    # Active participation
        4: 600,    # Regular contributor
        5: 1000,   # Career explorer
        6: 1500,   # Professional networker
        7: 2100,   # Industry insider
        8: 2800,   # Career strategist
        9: 3600,   # Mentor material
        10: 4500   # Career master
    }
    
    # Achievement criteria
    ACHIEVEMENTS = {
        'first_chat': {
            'title': 'First Steps',
            'description': 'Had your first career conversation',
            'points': 50
        },
        'chat_streak': {
            'title': 'Consistent Explorer',
            'description': 'Maintained a 5-day chat streak',
            'points': 100
        },
        'company_visit': {
            'title': 'Company Explorer',
            'description': 'Attended first company visit',
            'points': 150
        },
        'webinar_attendee': {
            'title': 'Knowledge Seeker',
            'description': 'Attended first exclusive webinar',
            'points': 120
        },
        'networking_pro': {
            'title': 'Networking Pro',
            'description': 'Connected with 5 other users',
            'points': 200
        }
    }
    
    @staticmethod
    def calculate_level(experience):
        """Calculate user level based on experience points"""
        for level, threshold in sorted(ProgressTracker.LEVEL_THRESHOLDS.items(), reverse=True):
            if experience >= threshold:
                return level
        return 1
    
    @staticmethod
    def experience_for_next_level(current_experience):
        """Calculate experience needed for next level"""
        current_level = ProgressTracker.calculate_level(current_experience)
        if current_level >= 10:  # Max level
            return None
        
        next_threshold = ProgressTracker.LEVEL_THRESHOLDS[current_level + 1]
        return next_threshold - current_experience
    
    @staticmethod
    def check_achievements(user):
        """Check and award new achievements for a user"""
        new_badges = []
        
        # Check first chat achievement
        if user.chat_history and not user.has_badge('first_chat'):
            badge = Badge.query.filter_by(name='first_chat').first()
            if badge:
                user.badges.append(badge)
                new_badges.append(badge)
                user.add_experience(ProgressTracker.ACHIEVEMENTS['first_chat']['points'])
        
        # Check chat streak
        streak = ProgressTracker.calculate_chat_streak(user)
        if streak >= 5 and not user.has_badge('chat_streak'):
            badge = Badge.query.filter_by(name='chat_streak').first()
            if badge:
                user.badges.append(badge)
                new_badges.append(badge)
                user.add_experience(ProgressTracker.ACHIEVEMENTS['chat_streak']['points'])
        
        # Check company visit achievement
        if user.company_visits > 0 and not user.has_badge('company_visit'):
            badge = Badge.query.filter_by(name='company_visit').first()
            if badge:
                user.badges.append(badge)
                new_badges.append(badge)
                user.add_experience(ProgressTracker.ACHIEVEMENTS['company_visit']['points'])
        
        # Check webinar achievement
        if user.webinars_attended > 0 and not user.has_badge('webinar_attendee'):
            badge = Badge.query.filter_by(name='webinar_attendee').first()
            if badge:
                user.badges.append(badge)
                new_badges.append(badge)
                user.add_experience(ProgressTracker.ACHIEVEMENTS['webinar_attendee']['points'])
        
        # Check networking achievement
        if len(user.connections) >= 5 and not user.has_badge('networking_pro'):
            badge = Badge.query.filter_by(name='networking_pro').first()
            if badge:
                user.badges.append(badge)
                new_badges.append(badge)
                user.add_experience(ProgressTracker.ACHIEVEMENTS['networking_pro']['points'])
        
        if new_badges:
            db.session.commit()
        
        return new_badges
    
    @staticmethod
    def calculate_chat_streak(user):
        """Calculate user's current chat streak"""
        if not user.chat_history:
            return 0
        
        # Get chat history sorted by date
        chats = sorted(user.chat_history, key=lambda x: x.timestamp, reverse=True)
        
        streak = 0
        last_date = None
        
        for chat in chats:
            chat_date = chat.timestamp.date()
            
            if last_date is None:
                streak = 1
                last_date = chat_date
                continue
            
            # Check if this chat is from the previous day
            if (last_date - chat_date).days == 1:
                streak += 1
                last_date = chat_date
            elif (last_date - chat_date).days > 1:
                break
        
        return streak
    
    @staticmethod
    def get_progress_summary(user):
        """Get a summary of user's progress"""
        current_level = user.level
        current_exp = user.experience
        exp_for_next = ProgressTracker.experience_for_next_level(current_exp)
        
        summary = {
            'level': current_level,
            'experience': current_exp,
            'next_level_exp': exp_for_next,
            'progress_percentage': (current_exp - ProgressTracker.LEVEL_THRESHOLDS[current_level]) / 
                                 (ProgressTracker.LEVEL_THRESHOLDS[current_level + 1] - 
                                  ProgressTracker.LEVEL_THRESHOLDS[current_level]) * 100 if exp_for_next else 100,
            'badges': len(user.badges),
            'company_visits': user.company_visits,
            'webinars_attended': user.webinars_attended,
            'chat_streak': ProgressTracker.calculate_chat_streak(user),
            'total_chats': len(user.chat_history) if user.chat_history else 0,
            'connections': len(user.connections) if hasattr(user, 'connections') else 0
        }
        
        return summary
    
    @staticmethod
    def get_engagement_score(user):
        """Calculate user's engagement score based on various factors"""
        base_score = 0
        
        # Activity-based scoring
        base_score += len(user.chat_history) * 2  # 2 points per chat
        base_score += user.company_visits * 10    # 10 points per company visit
        base_score += user.webinars_attended * 8  # 8 points per webinar
        
        # Streak bonus
        streak = ProgressTracker.calculate_chat_streak(user)
        base_score += streak * 5  # 5 points per day of streak
        
        # Level bonus
        base_score += user.level * 15  # 15 points per level
        
        # Badge bonus
        base_score += len(user.badges) * 20  # 20 points per badge
        
        # Normalize score to 0-100 range
        normalized_score = min(100, math.ceil(base_score / 5))
        
        return normalized_score 