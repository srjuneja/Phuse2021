from flask import Blueprint, Flask, url_for, send_from_directory, request, abort, jsonify, redirect, flash, has_request_context, send_file
import logging, os, platform, io, subprocess
from werkzeug.utils import secure_filename

from time import strftime
# Classes
from configurations import config
from utilities import utility
import r.pyr as rservice

r = Blueprint("r", __name__, root_path="/r")

@r.route('/r', methods=['GET'])
def hello():
    return {"data": "Hello R Webservices!"}


@r.route("/r/run_rcode",methods=['POST'])
def r_code():
    if request.method == 'POST' and request.files['file']:
        # if folder does not exist, create the upload folder
        utility.create_new_folder(config.UPLOAD_FOLDER)
        # save the file in upload folder
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        saved_path = os.path.join(config.UPLOAD_FOLDER, filename)
        print("saving {}".format(saved_path))
        uploaded_file.save(saved_path)

        result = rservice.run_R(r_filepath=saved_path)
        print(result)

        return jsonify(result)


