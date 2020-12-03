# pylint: skip-file
"""create submissions table

Revision ID: 089e88cc3926
Revises: 
Create Date: 2020-11-30 18:38:16.024465

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as postgres
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '089e88cc3926'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'submission',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('formio_id', sa.VARCHAR(24), nullable=False),
        sa.Column('data', postgres.JSONB, nullable=False),
        sa.Column('date_created', sa.DateTime(timezone=True), server_default=func.now())
    )


def downgrade():
    op.drop_table('submission')
