import boto3
import os

from config import app_config
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from models import db, application, pwd_context
from models.Admin import Admin
from models.Employer import Employer
from models.JobPosting import JobPosting
from models.Student import Student
from models.UserFile import UserFile
from models.JobApplication import JobApplication

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
        if resp == 'Expired JWT' or resp == 'Invalid JWT':
            response = {
                'status': 'error',
                'message': resp
            }
            return response
        else:
            user = user_type.query.filter_by(id=resp).first()
            response = {
                'status': 'success',
                'data': {
                    'user_id': user.id,
                    'email': user.email
                }
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
        return response, 200
    except Exception as e:
        raise e
        response = jsonify({
            'status': 'error',
            'message': 'could not fetch job postings'
        })
        return response, 500

@application.route('/jobs/<job_id>', methods=['GET', 'PUT'])
def get_job(job_id):
    try:
        job_posting = JobPosting.get_job(job_id)
    except Exception as e:
        response = jsonify({
            'status': 'error',
            'message': 'could not find job posting'
        })
        return response, 404

    if request.method == 'PUT':
        auth = verify_auth(request, Employer)
        employer_id = auth['data']['user_id']
        if job_posting.author_id == employer_id:
            data = request.json
            try:
                job_posting.update(data)
                response = jsonify({
                    'status': 'success',
                    'job_posting': job_posting.json
                })
                return response, 200
            except Exception as e:
                response = jsonify({
                    'status': 'error',
                    'message': 'Could not update job posting'
                })
                return response, 500
        else:
            response = jsonify({
                'status': 'error',
                'message': 'User did not create this job posting'
            })
            return response, 401
    else:
        response = jsonify({
            'status': 'success',
            'data': job_posting.json
        })
        return response, 200

@application.route('/jobs/<job_id>/applications', methods=['GET'])
def get_applications(job_id):
    auth = verify_auth(request, Employer)
    employer_id = auth['data']['user_id']
    try:
        job_posting = JobPosting.get_job(job_id)
        if job_posting.author_id == employer_id:
            applications = JobApplication.query.filter_by(posting_id=job_id)
            response = jsonify({
                'status': 'success',
                'applications': [job_app.json for job_app in applications]
            })
            return response, 200
        else:
            response = jsonify({
                'status': 'error',
                'message': 'User did not create this job posting'
            })
            return response, 401
    except Exception as e:
        raise e
        response = jsonify({
            'status': 'error',
            'message': 'could not get applications'
        })
        return response, 401

@application.route('/application/<app_id>', methods=['DELETE'])
def delete_application(app_id):
    try:
        job_app = JobApplication.query.get(app_id)
        auth = verify_auth(request, Student)
        if auth['status'] == 'success':
            if job_app.applicant_id == auth['data']['user_id']:
                job_app.delete()
                response = jsonify({
                    'status': 'success'
                })
                return response, 200
        response = jsonify({
            'status': 'error',
            'message': 'user does not have permission to delete'
        })
        return response, 401
    except Exception as e:
        response = jsonify({
            'status': 'error',
            'message': 'could not find application'
        })
        return response, 404

@application.route('/employer/jobs', methods=['GET'])
def get_employer_postings():
    auth = verify_auth(request, Employer)
    if auth['status'] == 'success':
        employer = Employer.query.get(auth['data']['user_id'])
        job_postings = employer.job_postings
        response = jsonify({
            'status': 'success',
            'jobs': [job.json for job in job_postings]
        })
        return response, 200
    else:
        return jsonify(auth), 401

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
        return response, 200

@application.route('/employer/login', methods=['POST'])
def employer_login():
    data = request.json
    try:
        user = Employer.query.filter_by(email=data['email']).first()
        if user:
            if pwd_context.verify(data['password'], user.password):
                if not user.is_approved:
                    response = jsonify({
                        'status': 'error',
                        'message': 'account is not approved'
                    })
                    return response, 200
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
        response = jsonify({
            'status': 'error',
            'message': 'error loging in'
        })
        return response, 401

@application.route('/admin/create', methods=['POST'])
def create_admin_account():
    data = request.get_json()
    user = Admin.query.filter_by(email=data.get('email')).first()
    if not user:
        try:
            user = Admin(
                data['name'],
                data['email'],
                data['password'],
                data['position']
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
            response = jsonify({
                'status': 'error',
                'message': 'error creating account',
            })
            return response, 500
    else:
        response = jsonify({
            'status': 'error',
            'message': 'User already exists'
        })
        return response, 200

@application.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    try:
        user = Admin.query.filter_by(email=data['email']).first()
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
            'message': 'error logging in'
        })
        return response, 401

@application.route('/admin/employers', methods=['GET'])
def get_employer_list():
    auth = verify_auth(request, Admin)
    if auth['status'] == 'success':
        try:
            employers = Employer.get_all()
            response = jsonify({
                'status': 'success',
                'employers': [employer.json for employer in employers]
            })
            return response, 200
        except Exception as e:
            response = jsonify({
                'status': 'error',
                'message': 'could not fetch employers'
            })
            return response, 500
    else:
        return jsonify(auth), 401

@application.route('/admin/students', methods=['GET'])
def get_student_list():
    auth = verify_auth(request, Admin)
    if auth['status'] == 'success':
        try:
            students = Student.get_all()
            response = jsonify({
                'status': 'success',
                'students': [student.json for student in students]
            })
            return response, 200
        except Exception as e:
            response = jsonify({
                'status': 'error',
                'message': 'could not fetch students'
            })
            return response, 500
    else:
        return jsonify(auth), 401

@application.route('/employer/<id>/verify', methods=['GET'])
def verify_employer(id):
    auth = verify_auth(request, Admin)
    if auth['status'] == 'success':
        try:
            employer = Employer.query.get(id)
            employer.update({'is_approved': True})
            response = jsonify({
                'status': 'success'
            })
            return response, 200
        except Exception as e:
            response = jsonify({
                'status': 'error',
                'message': 'could not verify employer'
            })
            return response, 200
    else:
        return jsonify(auth), 401

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
            response = jsonify({
                'status': 'error',
                'message': 'Error creating account',
            })
            return response, 401
    else:
        response = jsonify({
            'status': 'error',
            'message': 'User already exists'
        })
        return response, 200

@application.route('/student/delete', methods=['DELETE'])
def delete_student_account():
    auth = verify_auth(request, Student)
    if auth['status'] == 'success':
        student = Student.query.get(auth['data']['user_id'])
        try:
            student.delete()
            response = jsonify({
                'status': 'success'
            })
            return response, 200
        except Exception as e:
            raise e
            response = jsonify({
                'status': 'error',
                'message': 'account could not be deleted'
            })
            return response, 500
    else:
        response = jsonify({
            'status': 'error',
            'message': 'invalid credentials'
        })
        return response, 401

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
        else:
            response = jsonify({
                'status': 'error',
                'message': 'user does not exist'
            })
            return response, 200
    except Exception as e:
        response = jsonify({
            'status': 'error',
            'message': 'error loging in'
        })
        return response, 401

@application.route('/jobs/<job_id>/apply', methods=['POST'])
def apply_to_job(job_id):
    auth = verify_auth(request, Student)
    if auth['status'] == 'success':
        data = request.json
        transcript = data.get('transcript', None)
        if not transcript: 
            transcript = None
        cover_letter = data.get('cover_letter', None)
        if not cover_letter:
            cover_letter = None
        resume = data.get('resume', None)
        if not resume:
            resume = None
        job_application = JobApplication(auth['data']['user_id'],
            job_id, resume, transcript, cover_letter
        )
        job_application.save()
        response = jsonify({
            'status': 'success'
        })
        return response, 200
    else:
        return jsonify(auth), 401

@application.route('/upload', methods=['POST'])
def upload_file():
    auth = verify_auth(request, Student)
    if auth['status'] == 'success':
        data = request.form
        data_file = request.files['file']
        try:
            user_file = UserFile(auth['data']['user_id'],
                data['file_type'], data_file, data['file_name'])
            user_file.save()
            response = jsonify({
                'status': 'success'
            })
            return response, 200
        except Exception as e:
            response = jsonify({
                'status': 'error',
                'message': 'Could not upload file'
            })
            return response, 500
    else:
        return jsonify(auth), 401


def get_file_from_s3(file_path):
    s3 = boto3.resource('s3',
        region_name='us-east-1',
        aws_access_key_id=os.environ['S3_ACCESS_KEY'],
        aws_secret_access_key=os.environ['S3_SECRET_KEY']
    )
    user_file = s3.Object('gtbioportal', file_path).get()
    return user_file

@application.route('/files/<file_id>', methods=['POST', 'GET', 'DELETE'])
def get_file(file_id):
    """Returns file with given id from location in S3.

    Uses authentication to check if requesting user is the
    student who uploaded thPUTe file or an employer that owns a
    job posting where an application exists containing this file
    """
    try:
        user_file = UserFile.query.get(file_id)
    except Exception as e:
        raise e
        response = jsonify({
            'status': 'error',
            'message': 'file not found'
        })
        return response, 404
    if request.method == 'POST':
        data = request.get_json()
        auth = verify_auth(request, Employer)
        try:
            job_app = JobApplication.query.get(data['application_id'])
            job_posting = job_app.job_posting
            if job_posting.author_id == auth['data']['user_id']:
                fdata = get_file_from_s3(user_file.location)
                response = make_response(fdata['Body'].read())
                response.headers['Content-Type'] = 'application/pdf'
                return response
        except Exception as e:
            response = jsonify({
                'status': 'error',
                'message': 'could not find application'
            })
            return response, 404
    elif request.method == 'GET':
        auth = verify_auth(request, Student)
        if auth['status'] == 'success':
            if user_file.author_id == auth['data']['user_id']:
                fdata = get_file_from_s3(user_file.location)
                response = make_response(fdata['Body'].read())
                response.headers['Content-Type'] = 'application/pdf'
                return response
        response = jsonify({
            'status': 'error',
            'message': 'access denied'
        })
        return reponse, 401
    else:
        auth = verify_auth(request, Student)
        if auth['status'] == 'success' and auth['data']['user_id'] == user_file.author_id:
            try:
                user_file.delete()
                response = jsonify({
                    'status': 'success'
                })
                return response, 200
            except Exception as e:
                response = jsonify({
                    'status': 'error',
                    'message': 'could not delete file'
                })
                return response, 500
        response = jsonify({
            'status': 'error',
            'message': 'user does not have permission to delete file'
        })
        return response, 401

@application.route('/student/files', methods=['GET'])
def get_files():
    auth = verify_auth(request, Student)
    if auth['status'] == 'success':
        student = Student.query.get(auth['data']['user_id'])
        files = student.user_files
        response = jsonify({
            'status': 'success',
            'files': [f.json for f in files]
        })
        return response, 200
    else:
        return jsonify(auth), 401

if __name__ == '__main__':
    application.run(debug=True)