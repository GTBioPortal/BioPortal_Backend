import datetime

from . import db, ma
from marshmallow import Schema, fields, pre_load, validate


class JobPosting(db.Model):
    __tablename__ = 'job_postings'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(128), nullable=False)
    start_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    description = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    resume = db.Column(db.Boolean, default=False)
    cover_letter = db.Column(db.Boolean, default=False)
    transcript = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('employers.id'))
    author = db.relationship('Employer', backref='job_postings', foreign_keys=[author_id])

    def __init__(self, data, author):
        self.title = data['title']
        self.company = data['company']
        self.description = data['description']
        self.resume = data['resume']
        self.transcript = data['transcript']
        self.cover_letter = data['cover_letter']
        self.author_id = author

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @property
    def json(self):
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
            'author': self.author_id
        }

    @staticmethod
    def get_all_jobs():
        return JobPosting.query.all()

    @staticmethod
    def get_job(id):
        return JobPosting.query.get(id)