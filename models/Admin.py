import datetime

from . import db
from . import pwd_context
from .utils import random_key


class Admin(db.Model):
    """Admin database schema

    Attributes:
        id (int): Unique id of admin
        name (str): Admin user's full name
        email (str): User's email address
        password (str): User's encrypted password
    """
    __tablename__ = 'admins'

    id = db.Column(db.String(16), primary_key=True, autoincrement=False,
        nullable=False)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    position = db.Column(db.String(64), nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, email, password, position):
        """
        Initializes Admin object with encrypted password using
        argon2 hash function. 

        Args:
            name (str): Full name of user
            email (str): Email address of user
            password (str): User's plain text password 
        """
        self.name = name
        self.email = email
        self.password = pwd_context.hash(password)
        self.position = position

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

    # TODO: make JWT encode and decode usable with 
    # Employer and Student classes rather than duplicating code
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

    @staticmethod
    def decode_auth_token(token):
        """
        TODO: comb

        Decodes and validates a JWT.

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
            return 'Expired JWT'
        except jwt.InvalidTokenError:
            return 'Invalid JWT'