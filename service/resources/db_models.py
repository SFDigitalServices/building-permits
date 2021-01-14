"""Database Models"""

from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as postgres
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

BASE = declarative_base()

class SubmissionModel(BASE):
    # pylint: disable=too-few-public-methods
    """Submission Model"""

    __tablename__ = 'submission'
    id = sa.Column('id', sa.Integer, primary_key=True)
    formio_id = sa.Column('formio_id', sa.VARCHAR(24), nullable=False)
    data = sa.Column('data', postgres.JSONB, nullable=False)
    date_created = sa.Column('date_created', sa.DateTime(timezone=True), server_default=func.now())

def create_submission(db_session, json_data):
    """helper function for creating a submission"""
    submission = None
    try:
        validate(json_data)
        submission = SubmissionModel(data=json_data, formio_id=json_data['_id'])
        db_session.add(submission)
        db_session.commit()
        return submission
    except SQLAlchemyError as sql_err:
        db_session.rollback()
        raise sql_err
    finally:
        db_session.close()

def validate(json_data):
    """enforce validation rules"""
    if '_id' not in json_data:
        raise Exception("Missing formio_id")
