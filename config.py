
import platform, os

#  CONFIGURATION PARAMETERS
SECRET_KEY="s@srpyth0nwebserv1ces"

MAX_CONTENT_LENGTH = 1024 * 1024 # 1 MB
PYTHON_UPLOAD_EXTENSIONS = ['.txt', '.log', '.doc', '.docx']

OS_TYPE = platform.system()
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
SAS_FOLDER = '{}/sas_dsets/'.format(PROJECT_HOME)
DB_FOLDER = '{}/sql_db'.format(PROJECT_HOME)
LOG_FILE = "server.log"

# Documentation - Swagger
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'

# DATABASE PARAMETERS
SQLALCHEMY_DATABASE_URI="sqlite:////{}/data.db".format(PROJECT_HOME)
SQLALCHEMY_TRACK_MODIFICATIONS = True