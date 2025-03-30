from app.models.models import Event, Company, User, GroupChat
from app import db
from datetime import datetime, timedelta
from app.utils.ai_chat import CareerAI
import random

class EventManager:
    @staticmethod
    def get_recommended_events(user):
        """Get personalized event recommendations for a user"""
        # Get user's recommended company type
        company_type = user.get_recommended_company_type()
        
        # Get upcoming events
        upcoming_events = Event.query.join(Company)\
            .filter(Event.date > datetime.utcnow(),
                   Event.level_required <= user.level,
                   Company.size == company_type if company_type else True)\
            .order_by(Event.date.asc())\
            .limit(5)\
            .all()
        
        return upcoming_events
    
    @staticmethod
    def get_available_webinars(user):
        """Get available webinars for user's level"""
        if not user.can_attend_webinars():
            return []
        
        webinars = Event.query\
            .filter(Event.event_type == 'webinar',
                   Event.date > datetime.utcnow(),
                   Event.level_required <= user.level)\
            .order_by(Event.date.asc())\
            .all()
        
        return webinars
    
    @staticmethod
    def register_for_event(user, event_id):
        """Register a user for an event"""
        event = Event.query.get(event_id)
        
        if not event:
            return False, "Event not found"
        
        if event.date < datetime.utcnow():
            return False, "Event has already passed"
        
        if event.level_required > user.level:
            return False, "Your level is too low for this event"
        
        if user in event.participants:
            return False, "Already registered for this event"
        
        if len(event.participants) >= event.max_participants:
            return False, "Event is full"
        
        # Add user to event
        event.participants.append(user)
        
        # Create or get group chat for event
        if not event.group_chat_id:
            group_chat = GroupChat(
                name=f"Event Chat: {event.title}",
                event_id=event.id
            )
            db.session.add(group_chat)
            db.session.flush()
            event.group_chat_id = group_chat.id
        
        # Add user to event's group chat
        group_chat = GroupChat.query.get(event.group_chat_id)
        if group_chat and user not in group_chat.members:
            group_chat.members.append(user)
        
        # Update user stats
        if event.event_type == 'company_visit':
            user.company_visits += 1
        elif event.event_type == 'webinar':
            user.webinars_attended += 1
        
        # Add experience points
        user.add_experience(event.points)
        
        db.session.commit()
        return True, "Successfully registered for event"
    
    @staticmethod
    def get_matching_buddies(user, event_id, limit=3):
        """Find matching buddies for an event"""
        event = Event.query.get(event_id)
        if not event:
            return []
        
        # Get other participants
        other_participants = User.query\
            .join(event_participants)\
            .filter(event_participants.c.event_id == event_id,
                   User.id != user.id)\
            .all()
        
        # Score participants based on common interests
        user_interests = set(user.interests.lower().split(',')) if user.interests else set()
        scored_participants = []
        
        for participant in other_participants:
            participant_interests = set(participant.interests.lower().split(',')) if participant.interests else set()
            common_interests = len(user_interests & participant_interests)
            scored_participants.append((participant, common_interests))
        
        # Sort by number of common interests
        scored_participants.sort(key=lambda x: x[1], reverse=True)
        
        return [p[0] for p in scored_participants[:limit]]
    
    @staticmethod
    def get_company_recommendations(user):
        """Get personalized company recommendations"""
        company_type = user.get_recommended_company_type()
        
        # Get companies matching user's level and interests
        companies = Company.query\
            .filter(Company.size == company_type if company_type else True)\
            .limit(10)\
            .all()
        
        # Score companies based on user interests
        user_interests = set(user.interests.lower().split(',')) if user.interests else set()
        scored_companies = []
        
        for company in companies:
            # Create a set of keywords from company description and industry
            company_keywords = set((company.description + ' ' + company.industry).lower().split())
            interest_match = len(user_interests & company_keywords)
            scored_companies.append((company, interest_match))
        
        # Sort by match score and return top companies
        scored_companies.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in scored_companies[:5]]
    
    @staticmethod
    def create_event_summary(event):
        """Create a summary of an event including participants and details"""
        summary = {
            'title': event.title,
            'description': event.description,
            'date': event.date.strftime('%Y-%m-%d %H:%M'),
            'duration': f"{event.duration} minutes",
            'company': event.company.name if event.company else None,
            'type': event.event_type,
            'participants': len(event.participants),
            'max_participants': event.max_participants,
            'level_required': event.level_required,
            'points': event.points,
            'has_group_chat': bool(event.group_chat_id)
        }
        return summary 