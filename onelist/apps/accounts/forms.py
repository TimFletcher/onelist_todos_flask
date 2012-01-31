import re

from postmark.core import PMMail
from flask import render_template, current_app, g
from wtforms import Form, TextField, PasswordField, validators
from wtforms.validators import ValidationError, StopValidation, Regexp

from onelist.email import mail_admins, send_mail
from onelist.apps.accounts.tokens import token_generator


from wtforms.widgets import Input

class EmailInput(Input):
    """Render a single-line text input.
    """
    input_type = 'email'


class Email(Regexp):
    """More comprehensive version of WTForms email validation. Stops validation
    if email is invalid. Regex sourced from Django.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        email_re = r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*" \
                   r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' \
                   r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$'
        super(Email, self).__init__(email_re, re.IGNORECASE, message)

    def __call__(self, form, field):
        if not self.regex.match(field.data or u''):
            if self.message is None:
                self.message = field.gettext(u'Invalid email address.')
            raise StopValidation(self.message)


class LoginForm(Form):
    """A form that adds form level validation. After all fields have passed
    validation a further validation of the login credentials takes place. If any
    fields fail validation, their errors are registered and the form level
    validation does not take place.
    """
    email = TextField('Email',
                      [validators.Required(message='Required'),
                       Email(message='Invalid Email')],
                      widget=EmailInput())
    password = PasswordField('Password', [validators.Required(message='Required')])

    def validate_form(self):
        user = g.User.authenticate(self.email.data, self.password.data)
        if user:
            self.user = user
        else:
            return u"Incorrect email and/or password"

    def validate(self):
        """Override WTForm's default validation to provide form level validation.
        """
        if not super(Form, self).validate():
            return False
        errors = self.validate_form()
        if errors: 
            self._errors = {'form_errors': errors}
            return False
        return True

    def get_user(self):
        """
        Return the user, if it exists, or an exception if it doesn't. This
        function should only be user to get the user after a successful login.
        """
        user = getattr(self, 'user', None)
        if user is None:
            raise Exception("No user exists in the form.")
        return user


class RegistrationForm(Form):
    email = TextField('Email',
                      [validators.Required(message='Required'),
                       validators.Email(message='Invalid Email')],
                      widget=EmailInput())
    password = PasswordField('Password', [validators.Required(message='Required')])
    confirm  = PasswordField('Confirm Password', [validators.Required(message='Required'),
                                              validators.EqualTo('password', message="Passwords must match")])

    def validate_email(form, field):
        if g.User.get(email=field.data):
            raise ValidationError(u'Email already in use.')

    def register_user(self):
        """Register a new user and an assign them a list. Send an email
        notification to site admins.
        """
        user = g.User.create(email=self.email.data, password=self.password.data)
        todo_list = g.List.create(user)
        mail_admins("A new user registered",
                    "The user's email was {0}.".format(user.email))
        return user


class PasswordResetForm(Form):
    email = TextField('Email',
                      [validators.Required(message='Required'),
                       validators.Email(message='Invalid Email')],
                      widget=EmailInput())

    def validate_email(form, field):
        if not g.User.get(email=field.data):
            raise ValidationError(u'Email address not registered.')

    def send_reset_email(self):
        user = g.User.get(email=self.data['email'])
        domain = current_app.config['DOMAIN']
        send_mail("Password reset on {0}".format(domain),
                  render_template('accounts/password_reset_request_email.txt',
                                  **{'token': token_generator.make_token(user),
                                     'domain': domain}),
                  user.email)


class PasswordChangeForm(Form):
    password = PasswordField('New Password', [validators.Required()])
    confirm  = PasswordField('Confirm New Password',
                             [validators.Required(message='Required'),
                             validators.EqualTo('password', message="Passwords must match!")])