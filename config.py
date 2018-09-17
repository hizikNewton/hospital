
import os
BASEDIR = os.path.abspath(os.path.dirname(__file__))
TOP_LEVEL_DIR = os.path.abspath(os.curdir)


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('OLURIN ANUOLUWAPO') or 'add-your-random-key-here'
    S3_BUCKET = os.environ.get('hospital-bucket')
    S3_KEY = os.environ.get('AKIAIGMAB7BCMVQLA6HQ')
    S3_SECRET = os.environ.get('xFcRsBXfHxPORuOTjM5avQ1X9mZwEO7qGcHiZMSs')
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])