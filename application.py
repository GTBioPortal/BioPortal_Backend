import os

from config import app_config
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, application, pwd_context
from models.JobPosting import JobPosting
from models.Employer import Employer


def verify_auth(request, user_type):
    """Gets JWT from request authorization header and verifies it

    Args:
        request (Flask.request): HTTP POST request
        user_type (object): Type of user to auth. Admin, Employer, or Student.
    Returns:
        Dictionary with user id and email or error message if JWT is invalid.
    """
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(' ')[1]
    else:
        auth_token = None
    if auth_token:
        resp = user_type.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            user = user_type.query.filter_by(id=resp).first()
            response = {
                'status': 'success',
                'data': {
                    'user_id': user.id,
                    'email': user.email
                }
            }
            return response
        response = {
            'status': 'error',
            'message': resp
        }
        return response
    else:
        response = {
            'status': 'error',
            'message': 'invalid JWT'
        }
        return response

@application.route('/ping/', methods=['GET'])
def index():
    return 'pong'

@application.route('/jobs/create', methods=['POST'])
def create_job():
    auth = verify_auth(request, Employer)
    if auth['status'] == 'success':
        data = request.json
        posting = JobPosting(data, auth['data']['user_id'])
        posting.save()
        response = jsonify({
            'status': 'success'
        })
        return response, 200
    else:
        return jsonify(auth), 401

# TODO: Make paginated
@application.route('/jobs/', methods=['GET'])
def get_all_jobs():
    try:
        job_postings = JobPosting.get_all_jobs()
        response = jsonify({
            'status': 'success',
            'jobs': [job.json for job in job_postings]
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

@application.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    data = request.json
    try:
        job_posting = JobPosting.get_job(job_id)
        response = jsonify({
            'status': 'success',
            'data': job_posting.json
        })
        response.status_code = 200
        return response
    except Exception as e:
        response = jsonify({
            'status': 'error',
            'message': 'could not find job'
        })
        response.status_code = 401
        return response


@application.route('/employer/create', methods=['POST'])
def create_employer_account():
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
            return response, 200
        except Exception as e:
            raise e
            response = jsonify({
                'status': 'error',
                'message': 'Error creating account',
                'error': str(e)
            })
            return response, 401
    else:
        response = jsonify({
            'status': 'error',
            'message': 'User already exists'
        })
        return response, 202

@application.route('/employer/login', methods=['POST'])
def employer_login():
    data = request.json
    try:
        user = Employer.query.filter_by(email=data['email']).first()
        if user:
            if pwd_context.verify(data['password'], user.password):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    response = jsonify({
                        'status': 'success',
                        'message': 'logged in',
                        'auth_token': auth_token.decode()
                    })
                    return response, 200
                else:
                    response = jsonify({
                        'status': 'error',
                        'message': 'authentication error'
                    })
                    return response, 401
            else:
                response = jsonify({
                    'status': 'error',
                    'message': 'invalid credentials'
                })
                return response, 401
    except Exception as e:
        raise e
        response = jsonify({
            'status': 'error',
            'message': 'error loging in'
        })
        return response, 401

@application.route('/student/create', methods=['POST'])
def create_student_account():
    data = request.json
    user = Student.query.filter_by(email=data.get('email')).first()
    if not user:
        try:
            user = Student(
                data['name'],
                data['email'],
                data['password'],
                data['class']
            )
            user.save()
            auth_token = user.encode_auth_token(user.id)
            response = jsonify({
                'status': 'success',
                'message': 'Account created',
                'auth_token': auth_token.decode()
            })
            return response, 200
        except Exception as e:
            raise e
            response = jsonify({
                'status': 'error',
                'message': 'Error creating account',
                'error': str(e)
            })
            return response, 401
    else:
        response = jsonify({
            'status': 'error',
            'message': 'User already exists'
        })
        return response, 202

@application.route('/student/login', methods=['POST'])
def student_login():
    data = request.json
    try:
        user = Student.query.filter_by(email=data['email']).first()
        if user:
            if pwd_context.verify(data['password'], user.password):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    response = jsonify({
                        'status': 'success',
                        'message': 'logged in',
                        'auth_token': auth_token.decode()
                    })
                    return response, 200
                else:
                    response = jsonify({
                        'status': 'error',
                        'message': 'authentication error'
                    })
                    return response, 401
            else:
                response = jsonify({
                    'status': 'error',
                    'message': 'invalid credentials'
                })
                return response, 401
    except Exception as e:
        raise e
        response = jsonify({
            'status': 'error',
            'message': 'error loging in'
        })
        return response, 401

if __name__ == '__main__':
    application.run(debug=True)