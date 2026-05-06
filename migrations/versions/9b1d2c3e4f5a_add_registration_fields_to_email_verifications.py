"""add registration fields to email verifications

Revision ID: 9b1d2c3e4f5a
Revises: 626e9326fbde
Create Date: 2026-05-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "9b1d2c3e4f5a"
down_revision = "626e9326fbde"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("email_verifications", sa.Column("username", sa.String(length=80), nullable=True))
    op.add_column("email_verifications", sa.Column("password", sa.String(length=256), nullable=True))
    op.add_column("email_verifications", sa.Column("phone", sa.String(length=20), nullable=True))


def downgrade():
    op.drop_column("email_verifications", "phone")
    op.drop_column("email_verifications", "password")
    op.drop_column("email_verifications", "username")
