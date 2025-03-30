from app.models.models import Badge
from app.utils.progress_tracker import ProgressTracker
from app import db

def init_badges():
    """Initialize default badges in the database"""
    for badge_key, badge_data in ProgressTracker.ACHIEVEMENTS.items():
        if not Badge.query.filter_by(name=badge_key).first():
            badge = Badge(
                name=badge_key,
                title=badge_data['title'],
                description=badge_data['description']
            )
            db.session.add(badge)
    
    try:
        db.session.commit()
        print("Default badges initialized successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing badges: {str(e)}")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        init_badges() 