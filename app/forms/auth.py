from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, URL, Optional
from app.models.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address'),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    
    INTEREST_CHOICES = [
        ('software_development', '💻 Software Development'),
        ('data_science', '📊 Data Science & Analytics'),
        ('ai_ml', '🤖 AI & Machine Learning'),
        ('cybersecurity', '🔒 Cybersecurity'),
        ('cloud_computing', '☁️ Cloud Computing'),
        ('devops', '⚙️ DevOps & Infrastructure'),
        ('web_development', '🌐 Web Development'),
        ('mobile_development', '📱 Mobile Development'),
        ('ui_ux', '🎨 UI/UX Design'),
        ('product_management', '📋 Product Management'),
        ('digital_marketing', '📢 Digital Marketing'),
        ('business_analytics', '📈 Business Analytics'),
        ('project_management', '📅 Project Management'),
        ('blockchain', '⛓️ Blockchain'),
        ('iot', '🔌 IoT'),
        ('ar_vr', '👓 AR/VR'),
        ('game_development', '🎮 Game Development'),
        ('technical_writing', '✍️ Technical Writing'),
        ('qa_testing', '🔍 QA & Testing'),
        ('database_admin', '🗄️ Database Administration')
    ]
    
    interests = SelectMultipleField('Career Interests',
        choices=INTEREST_CHOICES,
        validators=[DataRequired(message='Please select at least one interest')],
        coerce=str
    )
    
    terms = BooleanField('I agree to the Terms of Service and Privacy Policy', validators=[
        DataRequired(message='You must accept the terms to proceed')
    ])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('This email is already registered. Please use a different email or login.')

    def validate_interests(self, interests):
        if not interests.data:
            raise ValidationError('Please select at least one interest')
        if len(interests.data) > 10:
            raise ValidationError('You can select up to 10 interests')

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    linkedin_profile = StringField('LinkedIn Profile', validators=[Optional(), URL()])
    interests = SelectMultipleField('Career Interests', choices=[
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('marketing', 'Marketing'),
        ('design', 'Design'),
        ('engineering', 'Engineering'),
        ('business', 'Business'),
        ('science', 'Science'),
        ('arts', 'Arts')
    ])

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ]) 