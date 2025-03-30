from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.models import User, Event, Company
from app.utils.event_manager import EventManager
from app.utils.progress_tracker import ProgressTracker
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Home page route"""
    if current_user.is_authenticated:
        # Get upcoming events
        upcoming_events = Event.query.filter(
            Event.start_date >= db.func.current_date()
        ).order_by(Event.start_date).limit(3).all()
        
        # Get recommended users based on interests
        recommended_users = []
        if current_user.interests:
            recommended_users = User.query.filter(
                User.id != current_user.id,
                User.interests.overlap(current_user.interests)
            ).limit(3).all()
        
        return render_template('main/dashboard.html', 
                             upcoming_events=upcoming_events,
                             recommended_users=recommended_users)
    return render_template('main/index.html')

@main.route('/about')
def about():
    """About page route"""
    return render_template('main/about.html')

@main.route('/terms')
def terms():
    """Terms of service page route"""
    return render_template('main/terms.html')

@main.route('/privacy')
def privacy():
    """Privacy policy page route"""
    return render_template('main/privacy.html')

@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing personalized content and recommendations"""
    # Get user's progress and engagement
    progress_summary = ProgressTracker.get_progress_summary(current_user)
    engagement_score = ProgressTracker.get_engagement_score(current_user)
    
    # Get recommended events
    recommended_events = EventManager.get_recommended_events(current_user)
    
    # Get available webinars if user has access
    available_webinars = EventManager.get_available_webinars(current_user)
    
    # Get company recommendations
    recommended_companies = EventManager.get_company_recommendations(current_user)
    
    # Check for new achievements
    new_badges = ProgressTracker.check_achievements(current_user)
    if new_badges:
        for badge in new_badges:
            flash(f'🎉 New Achievement Unlocked: {badge.title}!')
    
    return render_template(
        'main/dashboard.html',
        progress=progress_summary,
        engagement_score=engagement_score,
        events=recommended_events,
        webinars=available_webinars,
        companies=recommended_companies
    )

@main.route('/profile')
@login_required
def profile():
    """User profile page"""
    progress_summary = ProgressTracker.get_progress_summary(current_user)
    engagement_score = ProgressTracker.get_engagement_score(current_user)
    
    return render_template(
        'main/profile.html',
        user=current_user,
        progress=progress_summary,
        engagement_score=engagement_score
    )

@main.route('/explore')
@login_required
def explore():
    """Explore page showing available opportunities"""
    # Get all upcoming events
    upcoming_events = Event.query\
        .filter(Event.date > datetime.utcnow())\
        .order_by(Event.date.asc())\
        .limit(10)\
        .all()
    
    # Get featured companies
    featured_companies = Company.query\
        .order_by(func.random())\
        .limit(6)\
        .all()
    
    # Get active users for networking
    active_users = User.query\
        .filter(User.id != current_user.id)\
        .order_by(User.last_active.desc())\
        .limit(8)\
        .all()
    
    return render_template(
        'main/explore.html',
        events=upcoming_events,
        companies=featured_companies,
        users=active_users
    )

@main.route('/connect/<int:user_id>', methods=['POST'])
@login_required
def connect_with_user(user_id):
    """Connect with another user"""
    if user_id == current_user.id:
        flash('You cannot connect with yourself!')
        return redirect(url_for('main.explore'))
    
    target_user = User.query.get_or_404(user_id)
    
    if target_user in current_user.connections:
        flash('You are already connected with this user!')
        return redirect(url_for('main.explore'))
    
    current_user.connections.append(target_user)
    db.session.commit()
    
    flash(f'You are now connected with {target_user.name}!')
    return redirect(url_for('main.explore'))

@main.route('/search')
def search():
    """Search page route"""
    query = request.args.get('q', '')
    if not query:
        return render_template('main/search.html')
    
    # Search for users
    users = User.query.filter(
        User.name.ilike(f'%{query}%') | 
        User.email.ilike(f'%{query}%')
    ).limit(10).all()
    
    # Search for events
    events = Event.query.filter(
        Event.title.ilike(f'%{query}%') |
        Event.description.ilike(f'%{query}%')
    ).limit(10).all()
    
    return render_template('main/search.html', 
                         query=query,
                         users=users,
                         events=events) 