import datetime
import jwt
import os

from . import db
from . import pwd_context
from .utils import random_key


class Employer(db.Model):
    """Employer database table.

    Attributes:
        id (int): Unique id of employer
        email (str): Employer's email address.
        password (str): Employer's encrypted password
        created_at (DateTime): User creation timestamp
        is_approved (bool): Boolean indicating if Employer account
            has been approved by an admin. Employers cannot login until approved.
        name (str): Employer's full name
        company (str): Name of company employer works for
        company_description (str): Short description of company employer works for
    """
    __tablename__ = 'employers'

    id = db.Column(db.String(16), primary_key=True, autoincrement=False,
        nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, 
        default=db.func.current_timestamp())
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String(64), nullable=False)
    company = db.Column(db.String(64), nullable=False)
    company_description = db.Column(db.Text, nullable=False)

    def __init__(self, name, email, password, company, company_description):
        """
        Initializes Employer object with encrypted password using
        argon2 has function.

        Args:
            name (str): Full name of user
            email (str): Email address of user
            password (str): User's plain text password
            company (str): Employer's company
            company_description (str): Short description of company employer
                works for
        """
        self.name = name
        self.email = email
        self.password = pwd_context.hash(password)
        self.company = company
        self.company_description = company_description

    def encode_auth_token(self, uid):
        """
        Generates a valid JWT for user with 2hr expiration.

        Args:
            uid (str): Unique id of user

        Returns:
            String containing encoded jwt for user, or error message
            if jwt could not be created.
        """
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

    @property
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'company': self.company,
            'company_description': self.company_description,
            'is_approved': self.is_approved,
            'job_postings': [posting.json for posting in self.job_postings]
        }
    
    # TODO: delete needs to also change relationship tables
    # e.g. also delete all job postings this user has created
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def decode_auth_token(token):
        """
        Decodes and validates a JWT

        Args:
            token (str): encoded JWT string to validate
        Returns:
            User's uid from the JWT sub field, or error message if
            jwt is expired or invalid
        """
        try:
            payload = jwt.decode(token, os.environ['SECRET_KEY'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Expired Signature'
        except jwt.InvalidTokenError:
            return 'Invalid JWT'