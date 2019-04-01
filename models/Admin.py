import datetime

from . import db
from . import pwd_context


class Admin(db.Model):
    """Admin database schema

    Attributes:
        id (int): Unique id of admin
        name (str): Admin user's full name
        email (str): User's email address
        password (str): User's encrypted password
    """
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)

    def __init__(self, name, email, password):
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