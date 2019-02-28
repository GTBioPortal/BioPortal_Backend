import datetime

from . import db


class Employer(db.Model):
    __tablename__ = 'employers'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String(64), nullable=False)
    company = db.Column(db.String(64), nullable=False)
    company_description = db.Column(db.Text, nullable=False)

    def __init__(self, name, email, password, company, company_description):
        self.name = name
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.company = company
        self.company_description = company_description

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
            return 'Expired Signature'
        except jwt.InvalidTokenError:
            return 'Invalid JWT'

