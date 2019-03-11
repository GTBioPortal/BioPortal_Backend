from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from passlib.context import CryptContext

import os

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)

ma = Marshmallow()

pwd_context = CryptContext(
    schemes=['argon2', 'pbkdf2_sha256'],
    deprecated='auto'
)

from .Admin import Admin
from .Application import Application
from .Employer import Employer
from .JobPosting import JobPosting
from .Student import Student