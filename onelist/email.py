from flask import current_app
from postmark.core import PMMail

def mail_admins(subject, message):
    PMMail(
        api_key   = current_app.config['POSTMARK_API_KEY'],
        sender    = current_app.config['DEFAULT_FROM_EMAIL'],
        to        = current_app.config['ADMIN_EMAIL'],
        subject   = current_app.config['EMAIL_SUBJECT_PREFIX'] + subject,
        text_body = message
    ).send(current_app.config['POSTMARK_TEST_MODE'])


def send_mail(subject, message, to):
    PMMail(
        api_key   = current_app.config['POSTMARK_API_KEY'],
        sender    = current_app.config['DEFAULT_FROM_EMAIL'],
        to        = to,
        subject   = current_app.config['EMAIL_SUBJECT_PREFIX'] + subject,
        text_body = message
    ).send(current_app.config['POSTMARK_TEST_MODE'])