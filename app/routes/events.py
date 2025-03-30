from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.models import Event, Company, GroupChat, ChatMessage, User
from app.utils.event_manager import EventManager
from app.utils.progress_tracker import ProgressTracker
from app.utils.ai_chat import CareerAI
from app import db, socketio
from datetime import datetime, timedelta
from sqlalchemy import func

events_bp = Blueprint('events', __name__)

@events_bp.route('/events')
@login_required
def event_list():
    """List all available events and webinars"""
    # Get recommended events based on user level and interests
    recommended_events = EventManager.get_recommended_events(current_user)
    
    # Get available webinars if user has access
    available_webinars = EventManager.get_available_webinars(current_user)
    
    # Get events user is registered for
    registered_events = current_user.events_attending
    
    # Get company recommendations
    recommended_companies = EventManager.get_company_recommendations(current_user)
    
    return render_template(
        'events/list.html',
        recommended_events=recommended_events,
        available_webinars=available_webinars,
        registered_events=registered_events,
        recommended_companies=recommended_companies,
        can_attend_webinars=current_user.can_attend_webinars()
    )

@events_bp.route('/events/<int:event_id>')
@login_required
def event_detail(event_id):
    """Show detailed information about an event"""
    event = Event.query.get_or_404(event_id)
    
    # Get event summary
    event_summary = EventManager.create_event_summary(event)
    
    # Get matching buddies for the event
    matching_buddies = EventManager.get_matching_buddies(current_user, event_id)
    
    # Check if user is registered
    is_registered = current_user in event.participants
    
    # Get group chat messages if user is registered
    chat_messages = []
    if is_registered and event.group_chat_id:
        chat_messages = ChatMessage.query\
            .filter_by(group_chat_id=event.group_chat_id)\
            .order_by(ChatMessage.timestamp.asc())\
            .all()
    
    return render_template(
        'events/detail.html',
        event=event,
        summary=event_summary,
        matching_buddies=matching_buddies,
        is_registered=is_registered,
        chat_messages=chat_messages
    )

@events_bp.route('/events/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    """Register for an event"""
    success, message = EventManager.register_for_event(current_user, event_id)
    
    if success:
        # Check for new achievements after registration
        new_badges = ProgressTracker.check_achievements(current_user)
        if new_badges:
            for badge in new_badges:
                flash(f'🎉 New Achievement Unlocked: {badge.title}!')
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('events.event_detail', event_id=event_id))

@events_bp.route('/events/<int:event_id>/chat', methods=['POST'])
@login_required
def event_chat(event_id):
    """Send a message in the event group chat"""
    event = Event.query.get_or_404(event_id)
    
    if not event.group_chat_id or current_user not in event.participants:
        return jsonify({'error': 'Access denied'}), 403
    
    message_content = request.json.get('message')
    if not message_content:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    message = ChatMessage(
        content=message_content,
        user_id=current_user.id,
        group_chat_id=event.group_chat_id
    )
    db.session.add(message)
    db.session.commit()
    
    # Emit the message to all participants
    socketio.emit(
        'event_message',
        {
            'message': message_content,
            'user': current_user.name,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        },
        room=f'event_{event_id}'
    )
    
    return jsonify({'status': 'success'})

@events_bp.route('/companies')
@login_required
def company_list():
    """List available companies for visits"""
    # Get recommended companies based on user level and interests
    recommended = EventManager.get_company_recommendations(current_user)
    
    # Get all companies with upcoming events
    companies_with_events = Company.query\
        .join(Event)\
        .filter(Event.date > datetime.utcnow())\
        .distinct()\
        .all()
    
    # Get company type based on user level
    recommended_type = current_user.get_recommended_company_type()
    
    return render_template(
        'events/companies.html',
        recommended_companies=recommended,
        companies_with_events=companies_with_events,
        recommended_type=recommended_type
    )

@events_bp.route('/companies/<int:company_id>')
@login_required
def company_detail(company_id):
    """Show detailed information about a company"""
    company = Company.query.get_or_404(company_id)
    
    # Get upcoming events for this company
    upcoming_events = Event.query\
        .filter_by(company_id=company_id)\
        .filter(Event.date > datetime.utcnow())\
        .order_by(Event.date.asc())\
        .all()
    
    # Get AI insights about the company
    ai = CareerAI(current_user)
    company_insights = ai.generate_response(
        f"Tell me about {company.name} in the {company.industry} industry. "
        f"What makes them interesting for someone with interests in {current_user.interests}?"
    )
    
    return render_template(
        'events/company_detail.html',
        company=company,
        upcoming_events=upcoming_events,
        company_insights=company_insights
    )

@socketio.on('join_event_chat')
def on_join_event_chat(data):
    """Join event chat room"""
    event_id = data.get('event_id')
    event = Event.query.get(event_id)
    
    if event and current_user in event.participants:
        room = f'event_{event_id}'
        socketio.join_room(room)
        socketio.emit(
            'status',
            {'msg': f'{current_user.name} has joined the chat.'},
            room=room
        )

@socketio.on('leave_event_chat')
def on_leave_event_chat(data):
    """Leave event chat room"""
    event_id = data.get('event_id')
    room = f'event_{event_id}'
    socketio.leave_room(room)
    socketio.emit(
        'status',
        {'msg': f'{current_user.name} has left the chat.'},
        room=room
    )

@events_bp.route('/events/register/<int:event_id>', methods=['POST'])
@login_required
def register_event_old(event_id):
    """Register for an event"""
    event = Event.query.get_or_404(event_id)
    
    if event in current_user.registered_events:
        flash('You are already registered for this event!')
        return redirect(url_for('events.event_detail', event_id=event_id))
    
    if event.start_date < datetime.utcnow():
        flash('This event has already started!')
        return redirect(url_for('events.event_detail', event_id=event_id))
    
    if event.capacity and len(event.participants) >= event.capacity:
        flash('This event is already at full capacity!')
        return redirect(url_for('events.event_detail', event_id=event_id))
    
    current_user.registered_events.append(event)
    db.session.commit()
    
    flash(f'Successfully registered for {event.title}!')
    return redirect(url_for('events.event_detail', event_id=event_id))

@events_bp.route('/events/unregister/<int:event_id>', methods=['POST'])
@login_required
def unregister_event(event_id):
    """Unregister from an event"""
    event = Event.query.get_or_404(event_id)
    
    if event not in current_user.registered_events:
        flash('You are not registered for this event!')
        return redirect(url_for('events.event_detail', event_id=event_id))
    
    if event.start_date < datetime.utcnow():
        flash('Cannot unregister from a past event!')
        return redirect(url_for('events.event_detail', event_id=event_id))
    
    current_user.registered_events.remove(event)
    db.session.commit()
    
    flash(f'Successfully unregistered from {event.title}')
    return redirect(url_for('events.event_detail', event_id=event_id))

@events_bp.route('/events/my-events')
@login_required
def my_events():
    """Show user's registered events"""
    upcoming_events = Event.query.filter(
        Event.id.in_([e.id for e in current_user.registered_events]),
        Event.start_date >= datetime.utcnow()
    ).order_by(Event.start_date).all()
    
    past_events = Event.query.filter(
        Event.id.in_([e.id for e in current_user.registered_events]),
        Event.start_date < datetime.utcnow()
    ).order_by(Event.start_date.desc()).all()
    
    return render_template('events/my_events.html',
                         upcoming_events=upcoming_events,
                         past_events=past_events)

@events_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create a new event"""
    if not current_user.is_company_admin:
        flash('You do not have permission to create events!')
        return redirect(url_for('events.index'))
    
    if request.method == 'POST':
        event = Event(
            title=request.form['title'],
            description=request.form['description'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M'),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M'),
            location=request.form['location'],
            capacity=int(request.form['capacity']) if request.form['capacity'] else None,
            company_id=current_user.company_id,
            event_type=request.form['event_type'],
            is_virtual=bool(request.form.get('is_virtual')),
            registration_deadline=datetime.strptime(request.form['registration_deadline'], '%Y-%m-%dT%H:%M')
            if request.form['registration_deadline'] else None
        )
        db.session.add(event)
        db.session.commit()
        
        flash(f'Successfully created event: {event.title}')
        return redirect(url_for('events.event_detail', event_id=event.id))
    
    return render_template('events/create.html') 