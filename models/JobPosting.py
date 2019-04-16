import datetime

from . import db, ma
from .utils import random_key
from marshmallow import Schema, fields, pre_load, validate


class JobPosting(db.Model):
    """Job Posting database schema

    Attributes:
        id (int): Unique id of Job Posting
        title (str): Postion title 
        company (str): Company hiring for this position
        start_date (DateTime): Anticipated start date of this position
        description (str): Detailed description of this position
        deadline (DateTime): Deadline to accept applications until
        created_at (DateTime): Timestamp when employer created this job posting.
        resume (bool): Indicates if resume must be included with application
        cover_letter (bool): Indicates if cover letters must be included with
            applications.
        transcript (boot): Indicates if transcripts must be included with
            applications.
        author_id (int): ID of Employer who created this job posting.
        author (Employer): Employer who created this job posting.
    """
    __tablename__ = 'job_postings'

    id = db.Column(db.String(16), primary_key=True, autoincrement=False,
        nullable=False)
    title = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(128), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    resume = db.Column(db.Boolean, default=False)
    cover_letter = db.Column(db.Boolean, default=False)
    transcript = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.String(16), db.ForeignKey('employers.id'))
    author = db.relationship('Employer', backref='job_postings',
        foreign_keys=[author_id])

    def __init__(self, data, author):
        self.title = data['title']
        self.company = data['company']
        self.description = data['description']
        self.resume = data['resume']
        self.transcript = data['transcript']
        self.cover_letter = data['cover_letter']
        self.author_id = author
        self.start_date = datetime.datetime.strptime(data['start_date'],
            '%Y-%m-%dT%H:%M:%S.%fZ')
        self.deadline = datetime.datetime.strptime(data['deadline'],
            '%Y-%m-%dT%H:%M:%S.%fZ')
        self.location = data['location']

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
        db.session.delete(self)
        db.session.commit()

    @property
    def json(self):
        """Returns only necessary attributes for front-end rendering
        """
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'start_date': self.start_date,
            'description': self.description,
            'created_at': self.created_at,
            'resume': self.resume,
            'cover_letter': self.cover_letter,
            'transcript': self.transcript,
            'author': self.author_id,
            'deadline': self.deadline,
            'location': self.location
        }

    @staticmethod
    def get_all_jobs():
        """Returns list of all JobPostings in database
        """
        return JobPosting.query.all()

    @staticmethod
    def get_job(id):
        """Returns single JobPosting from database from it's uid.

        Args:
            id (str): uid of JobPosting to retrieve from db.
        """
        return JobPosting.query.get(id)