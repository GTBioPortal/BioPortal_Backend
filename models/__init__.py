from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)

ma = Marshmallow()

from .Admin import Admin
from .Application import Application
from .Employer import Employer
from .JobPosting import JobPosting, JobPostingSchema
from .Student import Student