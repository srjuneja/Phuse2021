import rpy2.robjects.packages as rpackages
import rpy2.robjects as robjects
from rpy2.robjects.vectors import StrVector
from subprocess import Popen, PIPE
from flask import jsonify

# https://rpy2.github.io/doc/v3.0.x/html/introduction.html
def install_rpackage(packnames):
    utils = rpackages.importr("utils")
    names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
    if len(names_to_install) > 0:
        utils.install_packages(StrVector(names_to_install))

#  TEST CALL
# install_rpackage(packnames=("ggplot2", "hexbin"))
# https://stackoverflow.com/questions/55841605/how-to-run-r-script-in-python-using-rpy2
def run_R(r_filepath, *args):

    arguments=[r_filepath]
    for arg in args:
        arguments.append(arg)
    # print(arguments)

    # COMMAND WITH ARGUMENTS
    # subprocess.call(['Rscript', 'script.R', arg1, arg2, arg3])
    # cmd = ["Rscript", "--vanilla", r_filepath,'/home/sajune/r_workspace/testgraph.jpg']
    cmd = ["Rscript", "--vanilla"] + arguments
    print (cmd)
    p = Popen(cmd, cwd="/home/sajune/r_workspace", stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    output, error = p.communicate()

    # PRINT R CONSOLE OUTPUT (ERROR OR NOT)
    if p.returncode == 0:
        print('R OUTPUT:\n {0}'.format(output))
        return output
    else:
        print('R ERROR:\n {0}'.format(error))
        return error

#  TEST CALL
# run_R("/home/sajune/r_workspace/test_r1.R")
# run_R("/home/sajune/r_workspace/test_r1.R","arg1","arg2")
'''
# https://stackoverflow.com/questions/49922118/running-r-script-in-python
def run_R2(source_file):
    r = robjects.r
    output = r.source("/home/sajune/r_workspace/test_r1.R")
    print(output)
    # print(robjects.globalenv["a"])

run_R2("/home/sajune/r_workspace/test_r1.R")
'''