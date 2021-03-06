import datetime
import jwt
import os

from . import db
from . import pwd_context
from .utils import random_key


class Student(db.Model):
    """Student database table.

    Attributes:
        id (int): Unique id of student
        email (str): Student's email address.
        password (str): Student's encrypted password
        class_standing (str): Student's current class (FR, SO, JR, or SR)
        name (str): Student's full name
    """
    __tablename__ = 'students'

    id = db.Column(db.String(16), primary_key=True, autoincrement=False,
        nullable=False)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    class_standing = db.Column(db.String(2), nullable=False)

    def __init__(self, name, email, password, class_standing):
        """
        Initializes Student object with encrypted password using
        argon2 has function.

        Args:
            name (str): Full name of user
            email (str): Email address of user
            password (str): User's plain text password
            class_standing (str): Student's current class (FR, SO, JR, or SR)
        """
        self.name = name
        self.email = email
        self.class_standing = class_standing
        self.password = pwd_context.hash(password)
    
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
            raise e
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
            return 'Expired Token'
        except jwt.InvalidTokenError:
            return 'Invalid Token'