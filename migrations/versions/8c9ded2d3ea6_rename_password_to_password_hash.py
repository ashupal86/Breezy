"""rename password to password_hash

Revision ID: 8c9ded2d3ea6
Revises: 69498ad0df08
Create Date: 2024-03-29 23:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c9ded2d3ea6'
down_revision = '69498ad0df08'
branch_labels = None
depends_on = None


def upgrade():
    # Use batch mode for SQLite
    with op.batch_alter_table('user') as batch_op:
        # Create new password_hash column
        batch_op.add_column(sa.Column('password_hash', sa.String(length=255)))
        
        # Copy data from password to password_hash
        op.execute('UPDATE user SET password_hash = password')
        
        # Drop old password column
        batch_op.drop_column('password')
        
        # Add other new columns
        batch_op.add_column(sa.Column('avatar_url', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('linkedin_profile', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('last_seen', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('is_company_admin', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('company_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('reset_token', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('reset_token_expiry', sa.DateTime(), nullable=True))
        
        # Create foreign key for company_id
        batch_op.create_foreign_key(
            'fk_user_company', 'company',
            ['company_id'], ['id']
        )
        
        # Create unique constraint for reset_token
        batch_op.create_unique_constraint(
            'uq_user_reset_token', ['reset_token']
        )
        
        # Drop old columns
        batch_op.drop_column('last_active')
        batch_op.drop_column('company_visits')


def downgrade():
    # Use batch mode for SQLite
    with op.batch_alter_table('user') as batch_op:
        # Drop new columns
        batch_op.drop_constraint('fk_user_company', type_='foreignkey')
        batch_op.drop_constraint('uq_user_reset_token', type_='unique')
        batch_op.drop_column('reset_token_expiry')
        batch_op.drop_column('reset_token')
        batch_op.drop_column('company_id')
        batch_op.drop_column('is_company_admin')
        batch_op.drop_column('last_seen')
        batch_op.drop_column('linkedin_profile')
        batch_op.drop_column('avatar_url')
        
        # Recreate old columns
        batch_op.add_column(sa.Column('password', sa.String(length=200), nullable=False))
        batch_op.add_column(sa.Column('last_active', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('company_visits', sa.Integer(), nullable=True))
        
        # Copy data back
        op.execute('UPDATE user SET password = password_hash')
        
        # Drop new password_hash column
        batch_op.drop_column('password_hash')
