import boto3
import datetime
import os
import uuid

from . import db
from .utils import random_key
from sqlalchemy.orm import backref


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

    id = db.Column(db.String(16), primary_key=True, autoincrement=False,
        nullable=False)
    author_id = db.Column(db.String(16),
        db.ForeignKey('students.id', ondelete='CASCADE'),
        nullable=False)
    author = db.relationship('Student', 
        backref=backref('user_files', passive_deletes=True),
        foreign_keys=[author_id])
    uploaded_at = db.Column(db.DateTime, index=True,
        default=db.func.current_timestamp())
    document_type = db.Column(db.String(32), nullable=False)
    location = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)

    def __init__(self, author, document_type, document, name):
        supported_types = {'resume', 'cover_letter', 'transcript'}
        if document_type not in supported_types:
            raise ValueError('Invalid document type: Supported types are' +
                'cover_letter, resume, or transcript')
        try:
            s3 = boto3.resource('s3',
                region_name='us-east-1',
                aws_access_key_id=os.environ['S3_ACCESS_KEY'],
                aws_secret_access_key=os.environ['S3_SECRET_KEY']
            )
            key = 'documents/' + str(uuid.uuid4().hex[:32]) + '.pdf'
            s3.meta.client.upload_fileobj(document, 'gtbioportal', key)
            self.author_id = author
            self.document_type = document_type
            self.location = key
            self.name = name
        except Exception as e:
            raise e

    @property
    def json(self):
        return {
            'id': self.id,
            'document_type': self.document_type,
            'location': self.location,
            'name': self.name
        }

    def save(self):
        success = False
        attempts = 0
        while not success:
            self.id = random_key(16)
            if attempts > 4:
                raise TimeoutError("Too many attempts")
            db.session.add(self)
            try:
                db.session.commit()
                success = True
            except:
                attempts += 1
                db.session.rollback()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()
    
    def delete(self):
        s3 = boto3.resource('s3',
            region_name='us-east-1',
            aws_access_key_id=os.environ['S3_ACCESS_KEY'],
            aws_secret_access_key=os.environ['S3_SECRET_KEY']    
        )
        obj = s3.Object("gtbioportal", self.location)
        obj.delete()
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_documents_by_user(uid):
        """Returns all documents a user has uploaded

        Args:
            id (str): uid of UserFile to retrieve
        """
        return UserFile.query.filter_by(author_id=uid)