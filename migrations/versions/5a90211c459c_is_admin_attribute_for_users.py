"""is_admin attribute for users

Revision ID: 5a90211c459c
Revises: 
Create Date: 2019-04-24 21:37:13.877343

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a90211c459c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('app_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=120), nullable=True),
    sa.Column('value', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_app_info_key'), 'app_info', ['key'], unique=True)
    op.create_index(op.f('ix_app_info_value'), 'app_info', ['value'], unique=False)
    op.create_table('reminder_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reminder_category_name'), 'reminder_category', ['name'], unique=True)
    op.create_table('settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=120), nullable=True),
    sa.Column('value', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_settings_key'), 'settings', ['key'], unique=True)
    op.create_index(op.f('ix_settings_value'), 'settings', ['value'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('reg_date', sa.DateTime(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_reg_date'), 'user', ['reg_date'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('reminder',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=120), nullable=True),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('finish_date', sa.DateTime(), nullable=True),
    sa.Column('finished', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['reminder_category.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reminder_creation_date'), 'reminder', ['creation_date'], unique=False)
    op.create_index(op.f('ix_reminder_finish_date'), 'reminder', ['finish_date'], unique=False)
    op.create_index(op.f('ix_reminder_title'), 'reminder', ['title'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_reminder_title'), table_name='reminder')
    op.drop_index(op.f('ix_reminder_finish_date'), table_name='reminder')
    op.drop_index(op.f('ix_reminder_creation_date'), table_name='reminder')
    op.drop_table('reminder')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_reg_date'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_settings_value'), table_name='settings')
    op.drop_index(op.f('ix_settings_key'), table_name='settings')
    op.drop_table('settings')
    op.drop_index(op.f('ix_reminder_category_name'), table_name='reminder_category')
    op.drop_table('reminder_category')
    op.drop_index(op.f('ix_app_info_value'), table_name='app_info')
    op.drop_index(op.f('ix_app_info_key'), table_name='app_info')
    op.drop_table('app_info')
    # ### end Alembic commands ###
