import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, g, session, render_template, render_template_string, \
        request, jsonify
from onelist.config import ProductionConfig
from onelist.database import Connection
from onelist.logger import PostMarkEmailHandler
from onelist.apps.lists.models import ListModel, ListItemModel
from onelist.apps.accounts.models import UserModel

APP_NAME = 'onelist'

# A dict of modules in the format <module_name>: <url_prefix>
MODULES = {
    'accounts': '/accounts',
    'lists': '/list',
    'pages': ''
}

def create_app(config=None):
    """
    Create and return the Flask application. We use a factory here so that differing
    configurations can be specified based on the ``ENV`` environment variable. This
    is useful for testing.
    """
    app = Flask(APP_NAME)
    configure_app(app, config)
    configure_logging(app)
    configure_modules(app, MODULES)
    configure_extensions(app)
    configure_error_handlers(app)
    configure_before_request(app)
    configure_after_request(app)
    return app

def configure_app(app, config):
    """
    Configure the app using the production configuration unless explicitly
    overridden when calling the create_app generator function.
    """
    app.config.from_object(ProductionConfig)
    if config is not None:
        app.config.from_object(config)
    # print '*** Running in {0} mode ***'.format(app.config['ENVIRONMENT'])

def configure_logging(app):

    mail_handler = PostMarkEmailHandler(app)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s '
                                  '[in %(pathname)s:%(lineno)d]')

    # Set up to log debug messages to debug logging file
    debug_file_handler = RotatingFileHandler(app.config['LOG_FILE'],
                                             maxBytes=100000,
                                             backupCount=10)
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(formatter)
    app.logger.addHandler(debug_file_handler)

    # Set up to log error messages to error logging file
    # error_file_handler = RotatingFileHandler(app.config['ERROR_LOG'],
    #                                          maxBytes=100000,
    #                                          backupCount=10)
    # error_file_handler.setLevel(logging.ERROR)
    # error_file_handler.setFormatter(formatter)
    # app.logger.addHandler(error_file_handler)

def configure_modules(app, modules):
    """
    Automatically import and register all modules in the MODULES dictionary. The
    fromlist argument to __import__() is necessary to tell __import__() to return
    the onelist.apps.<module> so that it's module attribute is accessible.
    """
    for module, url_prefix in modules.items():
        app.register_module(
            __import__("onelist.apps.{0}".format(module), fromlist=['']).module,
            url_prefix = url_prefix
        )

def configure_extensions(app):
    pass

def configure_error_handlers(app):

    @app.errorhandler(403)
    def page_not_found(e):
        if request.is_xhr:
            return 'Sorry, not allowed', 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        if request.is_xhr:
            return 'Sorry, page not found', 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        if request.is_xhr:
            return 'Sorry, an error has occurred', 500
        return render_template('errors/500.html'), 500


def configure_before_request(app):
    @app.before_request
    def connect_db():
        g.db = Connection(app.config['DB_HOST'],
                          app.config['DB_NAME'],
                          app.config['DB_USER'],
                          app.config['DB_PASSWD'])

    @app.before_request
    def load_models():
        MODELS = (
            ('User', UserModel, 'accounts_user'),
            ('List', ListModel, 'lists_list'),
            ('ListItem', ListItemModel, 'lists_listitem')
        )
        for model, klass, table in MODELS:
            setattr(g, model, klass(g.db, table))


    @app.before_request
    def authentication():
        """Add user into the g object for logged in users.
        """
        email = session.get('email') if 'email' in session else None
        if email:
            g.user = g.User.get(email=email)
            g.user['hash'] = g.List.get(user_id=g.user.id).hash
            g.user['is_authenticated'] = True
        else:
            g.user = {'is_authenticated': False}
        g.user['is_anonymous'] = not g.user['is_authenticated']


def configure_after_request(app):
    @app.after_request
    def clean_up(response):
        g.db.close()
        return response