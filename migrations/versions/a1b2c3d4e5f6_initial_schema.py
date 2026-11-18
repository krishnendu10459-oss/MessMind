"""Initial schema for Mess Records, Prediction Logs, and Surplus Advisories

Revision ID: a1b2c3d4e5f6
Revises: 
Create Date: 2026-11-14 22:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Mess Records Table
    op.create_table(
        'mess_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('record_date', sa.Date(), nullable=False),
        sa.Column('day_of_week', sa.String(length=20), nullable=False),
        sa.Column('meal_type', sa.String(length=20), nullable=False),
        sa.Column('menu_name', sa.String(length=100), nullable=False),
        sa.Column('attendance', sa.Integer(), nullable=False),
        sa.Column('prepared_meals', sa.Integer(), nullable=False),
        sa.Column('consumed_meals', sa.Integer(), nullable=False),
        sa.Column('wasted_meals', sa.Integer(), nullable=False),
        sa.Column('waste_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('prepared_meals >= 0', name='chk_prepared_positive'),
        sa.CheckConstraint('consumed_meals >= 0', name='chk_consumed_positive'),
        sa.CheckConstraint('wasted_meals >= 0', name='chk_wasted_positive'),
        sa.CheckConstraint('consumed_meals <= prepared_meals', name='chk_consumed_le_prepared'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mess_records_meal_type'), 'mess_records', ['meal_type'], unique=False)
    op.create_index(op.f('ix_mess_records_record_date'), 'mess_records', ['record_date'], unique=False)

    # 2. Prediction Logs Table
    op.create_table(
        'prediction_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('prediction_date', sa.Date(), nullable=False),
        sa.Column('meal_type', sa.String(length=20), nullable=False),
        sa.Column('menu_name', sa.String(length=100), nullable=False),
        sa.Column('expected_attendance', sa.Integer(), nullable=False),
        sa.Column('predicted_meals', sa.Integer(), nullable=False),
        sa.Column('confidence_interval_min', sa.Integer(), nullable=True),
        sa.Column('confidence_interval_max', sa.Integer(), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('predicted_meals >= 0', name='chk_predicted_positive'),
        sa.CheckConstraint('expected_attendance >= 0', name='chk_attendance_positive'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Surplus Advisories Table
    op.create_table(
        'surplus_advisories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('record_id', sa.Integer(), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('meal_type', sa.String(length=20), nullable=False),
        sa.Column('surplus_quantity', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('food_safety_verified', sa.Boolean(), nullable=True),
        sa.Column('verified_by', sa.String(length=100), nullable=True),
        sa.Column('recipient_organization', sa.String(length=150), nullable=True),
        sa.Column('advisory_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('surplus_quantity >= 0', name='chk_surplus_positive'),
        sa.ForeignKeyConstraint(['record_id'], ['mess_records.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('surplus_advisories')
    op.drop_table('prediction_logs')
    op.drop_index(op.f('ix_mess_records_record_date'), table_name='mess_records')
    op.drop_index(op.f('ix_mess_records_meal_type'), table_name='mess_records')
    op.drop_table('mess_records')
