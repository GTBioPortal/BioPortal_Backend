import datetime

from . import db


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    applicant = db.Column(db.Integer, db.ForeignKey('students.id'))
    timestamp = db.Column(db.DateTime, index=True, default=db.func.current_timestamp())

    def __init__(self, applicant):
        self.applicant = applicant