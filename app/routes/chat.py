from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from app.models.models import ChatMessage, GroupChat, User, Event
from app.utils.ai_chat import CareerAI
from app.utils.progress_tracker import ProgressTracker
from app import db, socketio
from datetime import datetime
from sqlalchemy import func

chat = Blueprint('chat', __name__)

@chat.route('/chat')
@login_required
def index():
    """Show chat dashboard"""
    # Get user's group chats
    group_chats = GroupChat.query.filter(
        GroupChat.participants.contains(current_user)
    ).all()
    
    # Get AI chat history
    ai_messages = ChatMessage.query.filter_by(
        user_id=current_user.id,
        is_ai_chat=True
    ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
    
    return render_template('chat/index.html',
                         group_chats=group_chats,
                         ai_messages=ai_messages)

@chat.route('/chat/ai', methods=['GET', 'POST'])
@login_required
def ai_chat():
    """AI Career Advisor chat interface"""
    if request.method == 'POST':
        message = request.form.get('message')
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Save user message
        user_msg = ChatMessage(
            content=message,
            user_id=current_user.id,
            is_ai_chat=True,
            is_ai_message=False
        )
        db.session.add(user_msg)
        
        # Initialize AI and generate response
        career_ai = CareerAI(current_user)
        ai_response = career_ai.generate_response(message)
        
        # Save AI response
        ai_msg = ChatMessage(
            content=ai_response,
            user_id=current_user.id,
            is_ai_chat=True,
            is_ai_message=True
        )
        db.session.add(ai_msg)
        db.session.commit()
        
        return jsonify({
            'user_message': {
                'content': user_msg.content,
                'timestamp': user_msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            },
            'ai_response': {
                'content': ai_msg.content,
                'timestamp': ai_msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    
    # Get chat history
    messages = ChatMessage.query.filter_by(
        user_id=current_user.id,
        is_ai_chat=True
    ).order_by(ChatMessage.timestamp).all()
    
    return render_template('chat/ai_chat.html', messages=messages)

@chat.route('/chat/group/<int:chat_id>')
@login_required
def group_chat(chat_id):
    """Group chat interface"""
    chat = GroupChat.query.get_or_404(chat_id)
    
    # Check if user is participant
    if current_user not in chat.participants:
        flash('You are not a participant in this chat.')
        return redirect(url_for('chat.index'))
    
    messages = ChatMessage.query.filter_by(
        group_chat_id=chat_id
    ).order_by(ChatMessage.timestamp).all()
    
    return render_template('chat/group_chat.html',
                         chat=chat,
                         messages=messages)

@socketio.on('join')
def on_join(data):
    """Socket.IO event handler for joining a chat room"""
    room = data['room']
    join_room(room)
    emit('status', {'msg': f'{current_user.name} has joined the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    """Socket.IO event handler for leaving a chat room"""
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f'{current_user.name} has left the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    """Socket.IO event handler for new messages"""
    room = data['room']
    message = data['message']
    
    # Save message to database
    chat_message = ChatMessage(
        content=message,
        user_id=current_user.id,
        group_chat_id=int(room),
        is_ai_chat=False,
        is_ai_message=False
    )
    db.session.add(chat_message)
    db.session.commit()
    
    # Broadcast message to room
    emit('message', {
        'user': current_user.name,
        'message': message,
        'timestamp': chat_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }, room=room)

@chat.route('/chat/suggest_activity', methods=['GET'])
@login_required
def suggest_activity():
    """Get an AI-suggested interactive activity"""
    career_ai = CareerAI(current_user)
    activity = career_ai.suggest_activity()
    
    return jsonify({
        'status': 'success',
        'activity': activity
    })

@chat.route('/chat/history')
@login_required
def chat_history():
    """View detailed chat history with insights"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get paginated chat history
    history = ChatMessage.query\
        .filter_by(user_id=current_user.id, is_ai_chat=True)\
        .order_by(ChatMessage.timestamp.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Get engagement analytics
    engagement_by_date = db.session.query(
        func.date(ChatMessage.timestamp).label('date'),
        func.avg(ChatMessage.engagement_score).label('avg_engagement')
    ).filter_by(user_id=current_user.id, is_ai_chat=True)\
     .group_by(func.date(ChatMessage.timestamp))\
     .order_by(func.date(ChatMessage.timestamp).desc())\
     .limit(30)\
     .all()
    
    # Get most discussed topics
    topics = db.session.query(
        ChatMessage.topics,
        func.count(ChatMessage.id).label('count')
    ).filter_by(user_id=current_user.id, is_ai_chat=True)\
     .filter(ChatMessage.topics != None)\
     .group_by(ChatMessage.topics)\
     .order_by(func.count(ChatMessage.id).desc())\
     .limit(5)\
     .all()
    
    return render_template(
        'chat/history.html',
        history=history,
        engagement_data=engagement_by_date,
        top_topics=topics
    )

@socketio.on('typing')
def handle_typing_status(data):
    """Broadcast typing status to all users"""
    socketio.emit('typing_status', {
        'user': current_user.name,
        'is_typing': data['is_typing']
    })

@chat.route('/chat/export', methods=['POST'])
@login_required
def export_chat_history():
    """Export chat history as JSON"""
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')
    
    query = ChatMessage.query.filter_by(user_id=current_user.id, is_ai_chat=True)
    
    if start_date:
        query = query.filter(ChatMessage.timestamp >= start_date)
    if end_date:
        query = query.filter(ChatMessage.timestamp <= end_date)
    
    history = query.order_by(ChatMessage.timestamp.asc()).all()
    
    export_data = [{
        'timestamp': chat.timestamp.isoformat(),
        'message': chat.content,
        'response': chat.response,
        'sentiment_score': chat.sentiment_score,
        'engagement_score': chat.engagement_score,
        'topics': chat.topics
    } for chat in history]
    
    return jsonify(export_data) 