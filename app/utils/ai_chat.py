import os
import google.generativeai as genai
from datetime import datetime
import json
import random
from app.models.models import ChatHistory, User
from app import db

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

class CareerAI:
    def __init__(self, user):
        self.user = user
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat_history = []
        self.load_chat_history()
    
    def load_chat_history(self):
        """Load recent chat history for context"""
        history = ChatHistory.query.filter_by(user_id=self.user.id)\
            .order_by(ChatHistory.timestamp.desc())\
            .limit(5)\
            .all()
        
        self.chat_history = [
            {'role': 'user', 'content': h.message} if not h.is_ai else
            {'role': 'assistant', 'content': h.response}
            for h in reversed(history)
        ]
    
    def get_system_prompt(self):
        """Generate dynamic system prompt based on user profile"""
        return f"""You are a friendly and engaging career guidance AI assistant. 
        Adapt your responses to be appropriate for someone who is {self.user.age} years old.
        The user's interests include: {self.user.interests}
        Their career goals are: {self.user.goals}
        Current level: {self.user.level} (Beginner: 1-2, Intermediate: 3-4, Advanced: 5+)
        
        Keep responses engaging and interactive. Include occasional:
        - Career-related jokes or trivia
        - Mini-challenges or thought exercises
        - Relevant industry insights
        - Encouragement and positive reinforcement
        
        If the conversation gets long, suggest interactive activities like:
        - Career quizzes
        - Role-playing scenarios
        - Industry exploration games
        
        Remember previous interactions and build upon them.
        """
    
    def generate_response(self, message, include_activities=True):
        """Generate AI response with optional interactive elements"""
        try:
            # Add user message to history
            self.chat_history.append({'role': 'user', 'content': message})
            
            # Prepare the prompt
            prompt = self.get_system_prompt() + "\n\nUser: " + message
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'top_k': 40,
                    'max_output_tokens': 1024,
                }
            )
            
            ai_response = response.text.strip()
            
            # Add interactive elements if needed
            if include_activities and len(self.chat_history) % 5 == 0:
                activity = self.suggest_activity()
                ai_response += f"\n\n{activity}"
            
            # Save to chat history
            chat_entry = ChatHistory(
                user_id=self.user.id,
                message=message,
                response=ai_response,
                sentiment_score=0.0,  # TODO: Implement sentiment analysis
                engagement_score=self.calculate_engagement_score(message, ai_response),
                topics=self.extract_topics(message + " " + ai_response)
            )
            db.session.add(chat_entry)
            
            # Update user engagement
            self.user.chat_count += 1
            self.user.last_active = datetime.utcnow()
            self.user.engagement_score = (self.user.engagement_score * 0.8 + 
                                        chat_entry.engagement_score * 0.2)
            
            # Add experience points
            points_earned = int(chat_entry.engagement_score * 10)
            leveled_up = self.user.add_experience(points_earned)
            
            db.session.commit()
            
            # Add level up message if applicable
            if leveled_up:
                ai_response += f"\n\n🎉 Congratulations! You've reached level {self.user.level}!"
            
            return ai_response
            
        except Exception as e:
            print(f"Error generating AI response: {str(e)}")
            return "I apologize, but I'm having trouble processing that right now. Could you try rephrasing your message?"
    
    def suggest_activity(self):
        """Suggest an interactive activity based on user level and interests"""
        activities = [
            {
                'type': 'quiz',
                'text': "Let's take a quick career values quiz! Ready to discover what matters most to you professionally?"
            },
            {
                'type': 'roleplay',
                'text': "How about we practice an interview scenario? I can play the interviewer role!"
            },
            {
                'type': 'challenge',
                'text': "Here's a fun challenge: Can you describe your dream job in exactly 6 words?"
            },
            {
                'type': 'game',
                'text': "Want to play 'Two Truths and a Lie' about different careers in your field of interest?"
            }
        ]
        
        return random.choice(activities)['text']
    
    def calculate_engagement_score(self, message, response):
        """Calculate engagement score based on interaction quality"""
        score = 0.5  # Base score
        
        # Length-based scoring
        msg_length = len(message.split())
        if msg_length > 20:
            score += 0.2
        elif msg_length > 10:
            score += 0.1
        
        # Question-based scoring
        if '?' in message:
            score += 0.1
        
        # Keyword-based scoring
        career_keywords = ['career', 'job', 'work', 'industry', 'company', 'skill']
        for keyword in career_keywords:
            if keyword in message.lower():
                score += 0.05
        
        return min(1.0, score)  # Cap at 1.0
    
    def extract_topics(self, text):
        """Extract main topics from the conversation"""
        common_topics = [
            'career planning', 'job search', 'skill development',
            'interview prep', 'networking', 'industry insights',
            'company culture', 'work-life balance', 'professional growth'
        ]
        
        topics = []
        for topic in common_topics:
            if topic in text.lower():
                topics.append(topic)
        
        return ','.join(topics[:3])  # Limit to top 3 topics
    
    def get_joke(self):
        """Get a career-related joke"""
        jokes = [
            "Why did the developer quit his job? He didn't get arrays!",
            "What do you call a bear with no job? Un-bear-ployed!",
            "Why did the career counselor bring a ladder to work? To help people climb the corporate ladder!",
            "What did the AI say to the job seeker? 'Let me process your career options... byte by byte!'",
        ]
        return random.choice(jokes)
    
    def get_trivia(self):
        """Get career-related trivia"""
        trivia = [
            "Did you know? The average person changes careers (not just jobs) 5-7 times in their lifetime!",
            "Fun fact: The term 'salary' comes from the Latin word 'salarium,' meaning 'salt money' - Roman soldiers were paid in salt!",
            "Interesting: The first resume is believed to have been written by Leonardo da Vinci in 1482!",
            "Fact: Remote work has increased by 159% since 2009!",
        ]
        return random.choice(trivia) 