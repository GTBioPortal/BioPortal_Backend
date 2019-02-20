from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

application = Flask(__name__)
db = SQLAlchemy(application)

ma = Marshmallow()

from .JobPosting import JobPosting, JobPostingSchema
from .User import User, ExpiredToken