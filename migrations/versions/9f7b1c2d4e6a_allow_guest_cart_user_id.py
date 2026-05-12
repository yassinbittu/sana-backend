"""Allow guest cart user id

Revision ID: 9f7b1c2d4e6a
Revises: 44e867ae3ca5
Create Date: 2026-05-12 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "9f7b1c2d4e6a"
down_revision = "44e867ae3ca5"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("carts", schema=None) as batch_op:
        batch_op.alter_column(
            "user_id",
            existing_type=sa.Integer(),
            nullable=True,
        )


def downgrade():
    with op.batch_alter_table("carts", schema=None) as batch_op:
        batch_op.alter_column(
            "user_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
