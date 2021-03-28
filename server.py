
from flask import Flask, request,  jsonify,  flash, has_request_context, \
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
from configurations import config
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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
db = SQLAlchemy(app)

#  Register BluePrints
app.register_blueprint(python)
app.register_blueprint(r)
app.register_blueprint(sas)


# https://sean-bradley.medium.com/add-swagger-ui-to-your-python-flask-api-683bfbb32b36
# https://www.youtube.com/watch?v=mViFmjcDOoA
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    config.SWAGGER_URL,
    config.API_URL,
    config={
        'app_name': "Analytics WebServices"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=config.SWAGGER_URL)

if __name__ == '__main__':

    # avoid cyclic db import - https://stackoverflow.com/questions/56712921/access-db-from-a-separate-file-flask-sqlalchemy-python3
    from sqldb.sqllite_db import secure
    app.register_blueprint(secure)

    # https://medium.com/@soumendrak/run-nginx-as-a-service-in-windows-7d30a5b3d184 - syntax for wsgiserver call
    server = WSGIServer(bind_addr=("0.0.0.0", int(5000)), wsgi_app=app, numthreads=100)
    server.ssl_adapter = pyOpenSSLAdapter("./certs/server.crt", "./certs/server.key", None)

    try:
        print("Starting Server at :" + strftime("%H:%M:%S"))
        server.start()
    except KeyboardInterrupt:
        server.stop()
