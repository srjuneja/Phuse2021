
from flask import Flask, url_for, send_from_directory, request, abort, jsonify, redirect, flash, has_request_context, \
    send_file, make_response
import logging, os, platform, io, subprocess


from werkzeug.security import generate_password_hash, check_password_hash
from cheroot.wsgi import Server as WSGIServer
from cheroot.ssl.pyopenssl import pyOpenSSLAdapter

from flask_sqlalchemy import SQLAlchemy
from time import strftime
import uuid
import datetime
import jwt

from functools import wraps
from flask_swagger_ui import get_swaggerui_blueprint

# Classes
import config
from python.python_main import python
from r.r_main import r
from sas.sas_main import sas


# Majority of code used from - https://github.com/JamesMudidi/flask-api-upload-image/blob/master/server.py
# Details around upload - https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
# Good Information - https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
# how to use postman - https://roytuts.com/python-flask-rest-api-file-upload/

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
    '%(levelname)s in %(module)s: %(message)s'
)

app = Flask(__name__)
app.debug = True

file_handler = logging.FileHandler(config.LOG_FILE)
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    admin = db.Column(db.Boolean)


# https://geekflare.com/securing-flask-api-with-jwt/
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        # print(request)
        token = None
        # print(request.headers)
        # print("access token: {}".format(request.headers['x-access-tokens']))

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        # try:
        data = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        print("data: {}".format(data))
        current_user = Users.query.filter_by(public_id=data['public_id']).first()
        print("current user: {}".format(current_user.name))
        # except:
        #    return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator


@app.route("/register", methods=['GET', 'POST'])
def signup_user():
    print(request)
    data = request.get_json()
    print("data: {}".format(data))

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    print("user: {}".format(new_user))

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'registered successfully'})


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    print("request: {}".format(request))
    auth = request.authorization
    print("auth: {}".format(auth))

    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    user = Users.query.filter_by(name=auth.username).first()

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            config.SECRET_KEY, algorithm="HS256")
        print(token)
        # return jsonify({'token': token.decode('UTF-8')})
        return jsonify({'token': token})

    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})


@app.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    users = Users.query.all()
    print("size: {}".format(len(users)))

    result = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin

        result.append(user_data)

    return jsonify({'users': result})


#  Register BluePrints
app.register_blueprint(python)
app.register_blueprint(r)
app.register_blueprint(sas)

# https://sean-bradley.medium.com/add-swagger-ui-to-your-python-flask-api-683bfbb32b36
# https://www.youtube.com/watch?v=mViFmjcDOoA
### swagger specific ###
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    config.SWAGGER_URL,
    config.API_URL,
    config={
        'app_name': "Analytics WebServices"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=config.SWAGGER_URL)
### end swagger specific ###

if __name__ == '__main__':
    # https://medium.com/@soumendrak/run-nginx-as-a-service-in-windows-7d30a5b3d184 - syntax for wsgiserver call
    server = WSGIServer(bind_addr=("0.0.0.0", int(5000)), wsgi_app=app, numthreads=100)
    server.ssl_adapter = pyOpenSSLAdapter("./server.crt", "./server.key", None)

    # server = wsgiserver.WSGIServer(wsgi_app=app, host="0.0.0.0", port=5000, numthreads=100,
    #                                certfile="/server.crt", keyfile="/server.key")
    try:
        print("Starting Server at :" + strftime("%H:%M:%S"))
        server.start()
    except KeyboardInterrupt:
        server.stop()
