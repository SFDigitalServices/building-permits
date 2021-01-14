# pylint: skip-file
"""unique formio_id

Revision ID: a6ce6da96ac7
Revises: 089e88cc3926
Create Date: 2021-01-07 13:58:30.694044

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6ce6da96ac7'
down_revision = '089e88cc3926'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint("uq_submission_formioid", "submission", ["formio_id"])


def downgrade():
    op.drop_constraint("uq_submission_formioid", "submission")
