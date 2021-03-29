import logging, os, platform, subprocess
from time import strftime

#  Below three imports are required for WINDOWS OS
# from win32com import client
# import pythoncom
# import docx2pdf

from utilities import utility


#  Method 1 - simply use docx2pdf - works on Windows and MacOS
def win_docx2pdf(source_file):
    dest_file = os.path.splitext(source_file)[0] + ".pdf"
    print("source_file = {}, dest_file = {}".format(source_file, dest_file))
    #  Initialization required to avoid errors
    pythoncom.CoInitialize()
    #  Using docx2pdf convert word to pdf
    docx2pdf.convert(source_file, dest_file)
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
