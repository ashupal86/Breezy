from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.models import User, db
from app.forms.auth import LoginForm, RegistrationForm, ProfileForm, ForgotPasswordForm, ResetPasswordForm
from app.utils.progress_tracker import ProgressTracker
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import secrets

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    # Initialize form data for GET requests
    if request.method == 'GET':
        form.interests.data = []
    
    # Handle AJAX validation requests for each step
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        step = request.args.get('step', type=int)
        if step is None:
            return jsonify({'valid': False, 'errors': {'general': 'Invalid step'}})
        
        # Process form data
        if not form.validate():
            return jsonify({'valid': False, 'errors': form.errors})
        
        errors = {}
        
        # Step-specific validation
        if step == 0:  # Basic Information
            if not form.name.data:
                errors['name'] = 'Name is required'
            if not form.email.data:
                errors['email'] = 'Email is required'
            elif User.query.filter_by(email=form.email.data.lower()).first():
                errors['email'] = 'Email already registered'
                
        elif step == 1:  # Password
            if not form.password.data:
                errors['password'] = 'Password is required'
            elif len(form.password.data) < 8:
                errors['password'] = 'Password must be at least 8 characters long'
            if form.password.data != form.confirm_password.data:
                errors['confirm_password'] = 'Passwords must match'
                
        elif step == 2:  # Interests
            selected_interests = request.form.getlist('interests')
            if not selected_interests:
                errors['interests'] = 'Please select at least one interest'
            elif len(selected_interests) > 10:
                errors['interests'] = 'Maximum 10 interests allowed'
            form.interests.data = selected_interests
                
        elif step == 3:  # Terms
            if not form.terms.data:
                errors['terms'] = 'You must accept the terms and conditions'
        
        if errors:
            return jsonify({'valid': False, 'errors': errors})
        
        # If this is the final submission
        if step == 3:
            try:
                user = User(
                    name=form.name.data,
                    email=form.email.data.lower(),
                    interests=','.join(form.interests.data) if form.interests.data else None
                )
                user.set_password(form.password.data)
                
                db.session.add(user)
                db.session.commit()
                login_user(user)
                
                return jsonify({
                    'valid': True,
                    'redirect': url_for('main.dashboard')
                })
            except Exception as e:
                db.session.rollback()
                print(f"Error during registration: {str(e)}")
                return jsonify({
                    'valid': False,
                    'errors': {'general': 'An error occurred. Please try again.'}
                })
        
        # Step validation successful
        return jsonify({'valid': True})
    
    # Handle regular form submission (non-AJAX)
    if form.validate_on_submit():
        try:
            user = User(
                name=form.name.data,
                email=form.email.data.lower(),
                interests=','.join(form.interests.data) if form.interests.data else None
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            print(f"Error during registration: {str(e)}")
    
    return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page if next_page else url_for('main.dashboard'))
        flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if request.method == 'GET':
        form.name.data = current_user.name
        form.bio.data = current_user.bio
        form.linkedin_profile.data = current_user.linkedin_profile
        form.interests.data = current_user.interests.split(',') if current_user.interests else []
    
    if form.validate_on_submit():
        try:
            current_user.name = form.name.data
            current_user.bio = form.bio.data
            current_user.linkedin_profile = form.linkedin_profile.data
            current_user.interests = ','.join(form.interests.data) if form.interests.data else None
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'danger')
            print(f"Error updating profile: {str(e)}")
    
    return render_template('auth/profile.html', form=form)

def send_password_reset_email(user):
    """Send password reset email to user"""
    # Generate token
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
    db.session.commit()
    
    # TODO: Implement actual email sending
    # For now, just print the reset link
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    print(f"Password reset link: {reset_url}")

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset requests"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for instructions to reset your password.', 'info')
            return redirect(url_for('auth.login'))
        flash('Email address not found.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    return render_template('auth/forgot_password.html', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password using token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        flash('Invalid or expired reset link.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

@auth.route('/profile/progress')
@login_required
def view_progress():
    progress_summary = ProgressTracker.get_progress_summary(current_user)
    engagement_score = ProgressTracker.get_engagement_score(current_user)
    
    return render_template(
        'auth/progress.html',
        progress=progress_summary,
        engagement_score=engagement_score
    )

def allowed_file(filename):
    """Check if uploaded file has an allowed extension"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 