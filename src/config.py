import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = False

    MARSHMALLOW_STRICT = True
    MARSHMALLOW_DATEFORMAT = 'rfc'
    SECRET_KEY = 'test_key'
    SECURITY_LOGIN_SALT = 'test'
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_TRACKABLE = True
    SECURITY_PASSWORD_SALT = 'something_super_secret_change_in_production'
    WTF_CSRF_ENABLED = False
    SECURITY_LOGIN_URL = '/test/v1/login/'
    SECURITY_LOGOUT_URL = '/test/v1/logout/'
    # SECURITY_POST_LOGIN_VIEW = '/test/v1/admin/'
    SECURITY_POST_RESET_VIEW = '/test/v1/reset/'
    SECURITY_POST_CONFIRM_VIEW = '/#/home/Account-Confirmed'

    SECURITY_RESET_URL = '/test/v1/reset-password/'
    SECURITY_RESET_PASSWORD_TEMPLATE = 'reset.html'
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_RECOVERABLE = True

    AUTH_HEADER_NAME = 'authentication-token'
    MAX_AGE = 86400

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_DEBUG = True
    MAIL_USERNAME = 'saurabh@hellonomnom.com'
    MAIL_PASSWORD = ''
    MAIL_DEFAULT_SENDER = 'saurabh@hellonomnom.com'
    MAIL_MAX_EMAILS = 100
    MAIL_SUPPRESS_SEND = True

    @staticmethod
    def init_app(app):
        pass

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/lenme'


class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:rootroot@shopkare.cr6vdsnghjiq.ap-south-1.rds.amazonaws.com:3306/shopkare'
    ELASTICSEARCH_HOST = 'https://search-shopkare-uglxe5anod6mmilgmj4rla35c4.ap-south-1.es.amazonaws.com/'


class ProdConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URI') or \
                              'sqlite:///{}'.format(os.path.join(basedir, 'why-is-prod-here.db'))


configs = {
    'dev': DevConfig,
    'testing': TestConfig,
    'prod': ProdConfig,
    'default': DevConfig
}
