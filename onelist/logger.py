import sys
import logging
import traceback

from onelist.email import mail_admins

from flask import g, request

class PostMarkEmailHandler(logging.Handler):

    def __init__(self, app):
        self.app = app
        logging.Handler.__init__(self)

    def emit(self, record):
        if record.exc_info:
            exc_info = record.exc_info
            stack_trace = '\n'.join(traceback.format_exception(*record.exc_info))
        else:
            exc_info = "No execution info supplied"
            stack_trace = "No stack trace info supplied"
        subject = "Error - {exc_type}".format(**{'app_name': self.app.import_name,
                                                 'exc_type': exc_info[0]})
        message = stack_trace + "\n"
        message += "*" * 40
        message += "\n"

        # Get request information
        for attr in ['method', 'path', 'url', 'form', 'args']:
            message += "{0}: {1}\n".format(attr, getattr(request, attr, None))
        message += "User: {0}".format(g.user)

        mail_admins(subject, message)