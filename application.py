import os

from config import app_config
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, application
from models.JobPosting import JobPosting, JobPostingSchema
from models.Employer import Employer


@application.route('/ping/', methods=['GET'])
def index():
    return 'pong'

@application.route('/jobs/create', methods=['POST'])
def create_job():
    data = request.json
    posting = JobPosting(data)
    posting.save()
    response = jsonify({
        'status': 'success'
    })
    response.status_code = 200
    return response

# TODO: Make paginated
@application.route('/jobs/', methods=['GET'])
def get_all_jobs():
    try:
        job_postings = JobPosting.get_all_jobs()
        response = jsonify({
            'status': 'success',
            'jobs': JobPostingSchema(many=True).dump(job_postings).data
        })
        response.status_code = 200
        return response
    except Exception as e:
        raise e
        response = jsonify({
            'status': 'error',
            'message': 'could not fetch job postings'
        })
        response.status_code = 401
        return response

# TODO: Fix this to use /jobs/ route and
# where this method is used when request type is POST
# and above method used when request type is GET
@application.route('/jobs/get', methods=['POST'])
def get_job():
    data = request.json
    try:
        job_posting = JobPosting.get_job(data['id'])
        response = jsonify({
            'status': 'success',
            'data': job_posting
        })
        response.status_code = 200
        return response
    except Exception as e:
        response = jsonfiy({
            'status': 'error',
            'message': 'could not find job'
        })
        response.status_code = 401
        return response


@application.route('/account/create', methods=['POST'])
def create_account():
    data = request.json
    user = Employer.query.filter_by(email=data.get('email')).first()
    if not user:
        try:
            user = Employer(
                data['name'],
                data['email'],
                data['password'],
                data['company'],
                data['company_description']
            )
            user.save()
            auth_token = user.encode_auth_token(user.id)
            response = jsonify({
                'status': 'success',
                'message': 'Account created',
                'auth_token': auth_token.decode()
            })
            response.status_code = 200
            return response
        except Exception as e:
            response = jsonify({
                'status': 'error',
                'message': 'Error creating account'
            })
            response.status_code = 401
            return response
    else:
        response = jsonify({
            'status': 'error',
            'message': 'User already exists'
        })
        response.status_code = 202
        return response

@application.route('/account/login', methods=['POST'])
def login():
    data = request.json
    try:
        user = Employer.query.filter_by(email=data['email']).first()
        if user:
            if bcrypt.check_password_hash(user.password, data['password']):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    response = jsonify({
                        'status': 'success',
                        'message': 'logged in',
                        'auth_token': auth_token.decode()
                    })
                    response.status = 200
                    return response
                else:
                    response = jsonify({
                        'status': 'error',
                        'message': 'authentication error'
                    })
                    response.status = 401
                    return response
            else:
                response = jsonify({
                    'status': 'error',
                    'message': 'invalid credentials'
                })
                response.status = 401
                return response
    except Exception as e:
        response = jsonify({
            'status': 'error',
            'message': 'error loging in'
        })
        response.status = 401
        return response

if __name__ == '__main__':
    application.run(debug=True)