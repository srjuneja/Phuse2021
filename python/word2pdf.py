import logging, os, platform, subprocess
from time import strftime

#  Below three imports are required for WINDOWS OS
# from win32com import client
# import pythoncom
# import docx2pdf

# Below imports are required for Linux Ubuntu

import utility


#  Method 1 - simply use docx2pdf - works on Windows and MacOS
def win_docx2pdf(source_file):
    # location = os.path.dirname(source_file )    #/srv/volume1/data/eds
    # file_name = os.path.basename(source_file )  #eds_report.csv
    # file_name_without_ext = os.path.splitext(file_name)
    dest_file = os.path.splitext(source_file)[0] + ".pdf"
    print("source_file = {}, dest_file = {}".format(source_file, dest_file))
    #  Initialization required to avoid errors
    # pythoncom.CoInitialize()
    #  Using docx2pdf convert word to pdf
    # docx2pdf.convert(source_file, dest_file)
    # Once pdf file is generated, delete the source file
    utility.background_remove(source_file)

# Method 2 - using Windows DLLs
#  https://stackoverflow.com/questions/53077204/convert-microsoft-word-document-to-pdf-using-python
def win_word_pdf(source_file):
    global word

    dest_file = os.path.splitext(source_file)[0] + ".pdf"
    print("source_file = {}, dest_file = {}".format(source_file, dest_file))
    #  Initialization required to avoid errors
    # pythoncom.CoInitialize()

    try:
        # word = client.Dispatch("Word.Application")
        doc = word.Documents.Open(source_file)
        print (strftime("%H:%M:%S"), " " + source_file + " -> pdf ", os.path.relpath(dest_file))
        doc.SaveAs(dest_file, FileFormat = 17)
        doc.Close()
    except Exception as e:
        print (e)
    finally:
        word.Quit()

    # Once pdf file is generated, delete the source file
    utility.background_remove(source_file)


# https://stackoverflow.com/questions/50982064/converting-docx-to-pdf-with-pure-python-on-linux-without-libreoffice
def linux_word_pdf(source_file):
    pdf_location = os.path.dirname(source_file )

    cmd = 'libreoffice --headless --convert-to pdf {} --outdir {} --nocrashreport --nodefault --nofirststartwizard --nolockcheck --nologo --norestore'.format(
        source_file, pdf_location)
    print(cmd)
    cmd2 = cmd.split()
    print(cmd2)
    p = subprocess.Popen(cmd2, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    p.wait(timeout=10)
    stdout, stderr = p.communicate()
    if stderr:
        raise subprocess.SubprocessError(stderr)

    # Once pdf file is generated, delete the source file
    utility.background_remove(source_file)
