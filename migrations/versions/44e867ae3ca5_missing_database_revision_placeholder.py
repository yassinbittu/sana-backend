"""Placeholder for existing database revision

Revision ID: 44e867ae3ca5
Revises: 9b1d2c3e4f5a
Create Date: 2026-05-12 00:00:00.000000

This project database is already stamped with this revision, but the
original migration file is not present in the checkout. Keep this no-op
revision so Alembic can continue upgrading from existing local databases.
"""

revision = "44e867ae3ca5"
down_revision = "9b1d2c3e4f5a"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
