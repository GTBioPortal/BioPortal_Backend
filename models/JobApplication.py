import datetime

from . import db


class JobApplication(db.Model):
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    applicant = db.relationship('Student', backref='applications', foreign_keys=[applicant_id])
    timestamp = db.Column(db.DateTime, index=True, default=db.func.current_timestamp())

    def __init__(self, applicant):
        self.applicant_id = applicant