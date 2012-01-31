from flask import Module, render_template, flash, request, redirect, session, \
        url_for, current_app, g, abort
from onelist.apps.accounts.forms import LoginForm, RegistrationForm, \
        PasswordChangeForm, PasswordResetForm
from onelist.apps.accounts.helpers import login_required
from onelist.apps.accounts.tokens import token_generator
from onelist.email import mail_admins

module = Module(__name__, 'accounts')


@module.route('/login/', methods=['GET', 'POST'])
def login():
    """Check a user's credentials and, if valid, log them in. If a user
    is already logged in, redirect them to their list page.
    """
    forward = redirect(url_for('lists.list'))
    if 'email' in session:
        return forward
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # Form is valid - ease the user's passage by logging them in.
        user = form.get_user()
        session['email'] = user.email
        return forward
    return render_template('accounts/login.html', form=form)


@module.route('/logout/')
@login_required
def logout():
    """Log a user out and display an appropriate flash message.
    """
    if session.pop('email', None):
        flash("You've been successfully logged out.", category="info")
    return redirect(url_for('pages.homepage'))


@module.route('/register/', methods=['GET', 'POST'])
def register():
    """Register a new user, automatically them in and redirect to their list page.
    Send an email notification to site admins on a successful registration. 
    """
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = form.register_user()
        session['email'] = user.email
        flash("Thanks! We've created your account and automatically logged you "
              "in.", category='info')
        return redirect(url_for('lists.list'))
    return render_template('accounts/register.html', form=form)


@module.route('/password_change/', methods=['GET', 'POST'])
@login_required
def password_change():
    """Change a user's password
    """
    form = PasswordChangeForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            g.User.change_password(form.data['password'], g.user)
            msg = "Your password was successfully changed"
            category = "info"
        except Exception, e:
            msg = "There was an error changing your password. Please contact support."
            current_app.logger.error('There was an error changing the password of {0}'.format(g.user.email))
            category = "error"
        finally:
            flash(msg, category=category)
        return redirect(url_for('lists.list'))
    return render_template('accounts/password_change.html', form=form)


@module.route('/password_reset_request/', methods=['GET', 'POST'])
def password_reset_request():
    """Request email. If the email exists, send a link that will log in the user
    to the supplied email. Deny access if already logged in.
    """
    if g.user['is_authenticated']:
        abort(403)
    form = PasswordResetForm(request.form)
    if request.method == 'POST' and form.validate():
        form.send_reset_email()
        return redirect(url_for('accounts.password_reset_request_complete'))
    return render_template('accounts/password_reset_request.html', form=form)


@module.route('/password_reset_request_complete/', methods=['GET'])
def password_reset_request_complete():
    """Display message that a password reset request was completed successfully.
    Deny access if already logged in.
    """
    if g.user['is_authenticated']:
        abort(403)
    return render_template('accounts/password_reset_request_complete.html')


@module.route('/password_reset_request_confirm/<token>/', methods=['GET'])
def password_reset_request_confirm(token):
    """Reset a user's password. Deny access if token is invalid or user is
    already logged in.
    """
    original_token = token
    if g.user['is_authenticated']:
        abort(403)
    user = token_generator.check_token(token)
    if not user:
        return render_template('accounts/password_reset_request_unsuccessful.html')
    flash("We've automatically logged you in. Please change your password now!",
          category='info')
    session['email'] = user.email
    return redirect(url_for('lists.list'))