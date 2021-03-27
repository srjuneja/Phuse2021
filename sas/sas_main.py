from flask import Blueprint, url_for, send_from_directory, request, abort, jsonify, redirect, flash, has_request_context, send_file
import logging, os, platform, io, subprocess
from werkzeug.utils import secure_filename

from time import strftime
# Classes
import utility, config
import sas.word2sas as word2sas

sas = Blueprint("sas", __name__, root_path="/sas")

@sas.route('/sas', methods=['GET'])
def hello():
    return {"data": "Hello SAS Webservices!"}


@sas.route("/sas/word2sas", methods=['POST'])
def wordsas():
    if request.method == 'POST' and request.files['file']:
        # Check if the request is correct and has file
        utility.check_request_file(request=request, extensions=config.PYTHON_UPLOAD_EXTENSIONS)
        # if folder does not exist, create the upload folder
        utility.create_new_folder(config.UPLOAD_FOLDER)
        # save the file in upload folder
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        saved_path = os.path.join(config.UPLOAD_FOLDER, filename)
        print("saving {}".format(saved_path))
        uploaded_file.save(saved_path)

        word2sas.docx2sasdsets(file_path=saved_path,lib_folder=config.SAS_FOLDER)

        # Pass on control to download file function
        download_file = config.SAS_FOLDER + "word_tbl.sas7bdat"
        print(download_file)
        return_data = io.BytesIO()
        with open(download_file, 'rb') as fo:
            return_data.write(fo.read())
            return_data.seek(0)

        utility.background_remove(download_file)
        # https://www.digipres.org/formats/mime-types/#application/x-sas-data - MIME TYPE for SAS dataset
        return send_file(return_data,  mimetype='application/x-sas-data', attachment_filename="word_tbl.sas7bdat")

    else:
        return {"Error": "Input File is missing"}