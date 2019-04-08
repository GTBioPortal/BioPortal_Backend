import boto3
import datetime

from . import db


class UserFile(db.Model):
    """User File database schema. Contains metadata
    on user files, most importantly a reference
    to it's location in S3.

    Attributes:
        id (int): Unique id of file
        author_id (int): id of User that uploaded this document
        author (User): User that uploaded this document. Currently only supports Students
        uploaded_at (DateTime): Timestamp of when document was uploaded
        document_type (str): Type of document. Currently only supports 'resume',
            'cover_letter', or 'transcript'
        location (str): Location of document in S3.
        name (str): Name of document given by user
    """
    __tablename__ = 'user_files'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    author = db.relationship('Student', backref='user_files',
        foreign_keys=[author_id])
    uploaded_at = db.Column(db.DateTime, index=True,
        default=db.func.current_timestamp())
    document_type = db.Column(db.String(32), nullable=False)
    location = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)

    def __init__(self, author, document_type, document, fname, name):
        try:
            s3 = boto3.resource('s3',
                region_name='us-east-1',
                aws_access_key_id='AKIA5AXTRQ5NHOL2PKUD',
                aws_secret_access_key='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',
                config=Config(signature_version='s3v4')
            )
            data = document.read()
            s3.Bucket('documents').put_object(Key='fname', Body=data)
        except Exception as e:
            raise e