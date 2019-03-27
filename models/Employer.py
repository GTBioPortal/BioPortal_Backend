import datetime
import jwt
import os

from . import db
from . import pwd_context


class Employer(db.Model):
    """Employer database table.

    Attributes:
        id: A unique integer primary key
        email: A string of the employer's email address 
            (multiple users cannot use the same email address)
        password: Plaintext employer's password
        created_at: DateTime timestamp of user creation time/date
        is_approved: Boolean indicating if Employer account
            has been approved by an admin. Employers cannot login until approved.
        name: Employer's full name
        company: String containing name of company employer works for
        company_description: String containing short description of company
    """
    __tablename__ = 'employers'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, 
        default=db.func.current_timestamp())
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String(64), nullable=False)
    company = db.Column(db.String(64), nullable=False)
    company_description = db.Column(db.Text, nullable=False)

    def __init__(self, name, email, password, company, company_description):
        self.name = name
        self.email = email
        self.password = pwd_context.hash(password)
        self.company = company
        self.company_description = company_description

    """Creates a JWT for the employer with a 2hr expiration

    Args:
        uid: Employer's id
    """
    def encode_auth_token(self, uid):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
                'iat': datetime.datetime.utcnow(),
                'sub': uid
            }
            return jwt.encode(
                payload,
                os.environ['SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as e:
            return e

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()
    
    # TODO: delete needs to also change relationship tables
    # e.g. also delete all job postings this user has created
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def decode_auth_token(token):
        try:
            payload = jwt.decode(token, os.environ['SECRET_KEY'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Expired Signature'
        except jwt.InvalidTokenError:
            return 'Invalid JWT'