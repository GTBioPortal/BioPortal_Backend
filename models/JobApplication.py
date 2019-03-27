import datetime

from . import db


class JobApplication(db.Model):
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    applicant = db.relationship('Student', backref='applications',
        foreign_keys=[applicant_id])
    timestamp = db.Column(db.DateTime, index=True,
        default=db.func.current_timestamp())
    posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'))
    job_posting = db.relationship('JobPosting', backref='applications',
        foreign_keys=[posting_id])

    def __init__(self, applicant, job_posting):
        self.applicant_id = applicant
        self.posting_id = job_posting

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