"""Initial migration

Revision ID: 69498ad0df08
Revises: 
Create Date: 2024-03-19 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69498ad0df08'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create tables
    op.create_table('badge',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_badge'),
        sa.UniqueConstraint('name', name='uq_badge_name')
    )

    op.create_table('company',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('size', sa.String(length=20), nullable=True),
        sa.Column('logo', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_company')
    )

    op.create_table('group_chat',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_group_chat'),
        sa.UniqueConstraint('event_id', name='uq_group_chat_event_id')
    )

    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password', sa.String(length=200), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('interests', sa.Text(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('profile_picture', sa.String(length=200), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('experience', sa.Integer(), nullable=True),
        sa.Column('company_visits', sa.Integer(), nullable=True),
        sa.Column('webinars_attended', sa.Integer(), nullable=True),
        sa.Column('last_active', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_user'),
        sa.UniqueConstraint('email', name='uq_user_email')
    )

    op.create_table('chat_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('engagement_score', sa.Float(), nullable=True),
        sa.Column('topics', sa.String(length=200), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_chat_history_user'),
        sa.PrimaryKeyConstraint('id', name='pk_chat_history')
    )

    op.create_table('chat_message',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('group_chat_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['group_chat_id'], ['group_chat.id'], name='fk_chat_message_group_chat'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_chat_message_user'),
        sa.PrimaryKeyConstraint('id', name='pk_chat_message')
    )

    op.create_table('event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('level_required', sa.Integer(), nullable=True),
        sa.Column('points', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=20), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('group_chat_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='fk_event_company'),
        sa.ForeignKeyConstraint(['group_chat_id'], ['group_chat.id'], name='fk_event_group_chat'),
        sa.PrimaryKeyConstraint('id', name='pk_event')
    )

    op.create_table('user_badges',
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('badge_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['badge_id'], ['badge.id'], name='fk_user_badges_badge'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_user_badges_user')
    )

    op.create_table('user_connections',
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('connected_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['connected_user_id'], ['user.id'], name='fk_user_connections_connected_user'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_user_connections_user')
    )

    op.create_table('event_participants',
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], name='fk_event_participants_event'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_event_participants_user')
    )


def downgrade():
    op.drop_table('event_participants')
    op.drop_table('user_connections')
    op.drop_table('user_badges')
    op.drop_table('event')
    op.drop_table('chat_message')
    op.drop_table('chat_history')
    op.drop_table('user')
    op.drop_table('group_chat')
    op.drop_table('company')
    op.drop_table('badge')
