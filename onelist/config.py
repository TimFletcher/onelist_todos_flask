iport os

ROOT = os.path.dirname(os.path.abspath(__file__))

class Config(object):

    # App
    DEBUG = True
    SECRET_KEY = ****************
    ADMIN = 'tim@timothyfletcher.com'
    PASSWORD_RESET_DAYS = 1

    # Email
    EMAIL_SUBJECT_PREFIX = '****************'
    DEFAULT_FROM_EMAIL   = '****************'
    POSTMARK_API_KEY     = '****************'
    POSTMARK_SENDER      = '****************'
    POSTMARK_TEST_MODE   = False # Prints JSON to console if DEBUG = True
    ADMIN_EMAIL          = '****************'

class ProductionConfig(Config):

    DOMAIN = 'http://onelistapp.co'
    ENVIRONMENT = 'production'
    DEBUG = False
    TESTING = False
    POSTMARK_TEST_MODE = DEBUG

    # Logging
    LOG_FILE = os.path.join(ROOT, 'logs/production.log')

    # MySQL
    DB_HOST   = '127.0.0.1'
    DB_NAME   = '****************'
    DB_USER   = '****************'
    DB_PASSWD = '****************'

class TestingConfig(ProductionConfig):

    SECRET_KEY = ****************
    DOMAIN = 'http://localhost:5000'
    ENVIRONMENT = 'testing'
    DEBUG = False
    TESTING = True
    POSTMARK_TEST_MODE = True

    # MySQL
    DB_HOST   = 'localhost'
    DB_NAME   = '****************'
    DB_USER   = '****************'
    DB_PASSWD = '****************'


class DevelopmentConfig(ProductionConfig):

    DOMAIN = 'http://localhost:5000'
    ENVIRONMENT = 'development'
    DEBUG = True
    TESTING = False
    POSTMARK_TEST_MODE = True
    
    # MySQL
    DB_HOST   = 'localhost'
    DB_NAME   = '****************'
    DB_USER   = '****************'
    DB_PASSWD = '****************'

    LOG_FILE = os.path.join(ROOT, 'logs/development.log')
