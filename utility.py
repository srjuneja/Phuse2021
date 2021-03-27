from flask import Flask, url_for, send_from_directory, request, abort, jsonify, redirect, flash, has_request_context, send_file
import logging, os, platform, io
from werkzeug.utils import secure_filename
from multiprocessing import Process


def check_request_file(request, extensions):
    # check if the post request has the file part
    if 'file' not in request.files:
        # flash('No file part')
        return redirect(request.url)

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    # app.logger.info(filename)
    # if user does not select file, browser also
    # submit a empty part without filename
    if filename == '':
        # flash('No selected file')
        return redirect(request.url)

    #  if extension not valid, abort
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in extensions:
            abort(400)

def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

# https://stackoverflow.com/questions/11817182/uploading-multiple-files-with-flask
def upload_files(request, upload_folder):
    # if folder does not exist, create the upload folder
    create_new_folder(upload_folder)
    # save the file in upload folder
    # uploaded_file = request.files['file']
    # filename = secure_filename(uploaded_file.filename)
    # saved_path = os.path.join(config.UPLOAD_FOLDER, filename)
    # print("saving {}".format(saved_path))
    # uploaded_file.save(saved_path)

    files = request.files.getlist("file")
    for file in files:
        filename = secure_filename(file.filename)
        saved_path = os.path.join(upload_folder, filename)
        print("saving {}".format(saved_path))
        file.save(saved_path)

# https://stackoverflow.com/questions/24612366/delete-an-uploaded-file-after-downloading-it-from-flask
#  remove file using background process
def background_remove(path):
    task = Process(target=rm(path))
    task.start()

def rm(path):
    os.remove(path)
