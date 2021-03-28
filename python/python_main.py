from flask import Blueprint, Flask, url_for, send_from_directory, request, abort, jsonify, redirect, flash, \
    has_request_context, send_file
import logging, os, platform, io, subprocess
from werkzeug.utils import secure_filename

# Classes
from configurations import config
from utilities import utility
from python.word2pdf import linux_word_pdf, win_word_pdf


python = Blueprint("python", __name__, root_path="/python")

# file_handler = logging.FileHandler('server.log')
# python.logger.addHandler(file_handler)
# python.logger.setLevel(logging.INFO)


@python.route('/python', methods=['GET'])
def hello():
    return {"data": "Hello Python Webservices!"}


@python.route("/python/word2pdf", methods=['POST'])
def word2pdf():
    # app.logger.info(PROJECT_HOME)
    if request.method == 'POST' and request.files['file']:
        print(request.__dict__)
        # app.logger.info(app.config['UPLOAD_FOLDER'])
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

        # utility.upload_files(request=request, upload_folder=config.UPLOAD_FOLDER)

        if config.OS_TYPE.lower() == "windows":
            # Method 2 - using Windows DLLs
            win_word_pdf(saved_path)
        else:
            # Method 3 - Using LibreOffice for Linux
            linux_word_pdf(source_file=saved_path)

        # Pass on control to download file function
        download_file = os.path.splitext(filename)[0] + ".pdf"
        print(download_file)
        return redirect(url_for('python.download', filename=download_file))
        # return redirect(url_for('listfiles', filename=filename))
        # return send_from_directory(app.config['UPLOAD_FOLDER'],filename, as_attachment=True)
    else:
        return {"Error": "Input File is missing"}


@python.route('/downloadfile/<filename>')
def download(filename):
    download_file = config.UPLOAD_FOLDER + filename
    print("Download file - {}".format(download_file))

    return_data = io.BytesIO()
    with open(download_file, 'rb') as fo:
        return_data.write(fo.read())
        return_data.seek(0)

    utility.background_remove(download_file)

    return send_file(return_data, mimetype='application/pdf', attachment_filename=filename)


