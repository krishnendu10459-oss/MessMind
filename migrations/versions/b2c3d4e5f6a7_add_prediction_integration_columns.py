"""Add prediction integration columns (predicted_meals, estimated_surplus, prediction_error)

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-11-14 23:05:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('mess_records', sa.Column('predicted_meals', sa.Integer(), nullable=True))
    op.add_column('mess_records', sa.Column('estimated_surplus', sa.Integer(), nullable=True))
    op.add_column('mess_records', sa.Column('prediction_error', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('mess_records') as batch_op:
        batch_op.drop_column('prediction_error')
        batch_op.drop_column('estimated_surplus')
        batch_op.drop_column('predicted_meals')
