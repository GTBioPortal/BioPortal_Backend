import datetime

from . import db


class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    def encode_auth_token(self, uid):
        try:
            payload = {
                'expiration': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
                'issued_at': datetime.datetime.utcnow(),
                'uid': uid
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(token):
        try:
            payload = jwt.decode(token, app.config.get('SECRET_KEY'))
            return payload['uid']
        except jwt.ExpiredSignatureError:
            return 'Expired JWT'
        except jwt.InvalidTokenError:
            return 'Invalid JWT'