import datetime

from . import db


class JobApplication(db.Model):
    """Job Application database schema

    Attributes:
        id (int): Unique id of Job Application
        applicant_id (int): id of Student that applied
        applicant (Student): Student that created this application
        timestamp (DateTime): Timestamp when the student applied 
        posting_id (int): id of JobPosting this application was for
        job_posting (JobPosting): JobPosting that this application was for
    """
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
    resume_id = db.Column(db.Integer, db.ForeignKey('user_files.id'), 
        nullable=True)
    transcript_id = db.Column(db.Integer, db.ForeignKey('user_files.id'),
        nullable=True)
    cover_letter_id = db.Column(db.Integer, db.ForeignKey('user_files.id'),
        nullable=True)

    def __init__(self, applicant, job_posting, resume, 
        transcript, cover_letter):
        self.applicant_id = applicant
        self.posting_id = job_posting
        self.resume_id = resume
        self.transcript_id = transcript
        self.cover_letter_id = cover_letter

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
            'applicant': self.applicant.name,
            'timestamp': self.timestamp,
            'resume': self.resume_id,
            'cover_letter': self.cover_letter_id,
            'transcript': self.transcript_id
        }