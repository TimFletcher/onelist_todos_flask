from flask import Module, render_template, request, url_for, g, current_app, \
        redirect

module = Module(__name__, 'pages')

@module.route('/')
def homepage(methods=['GET']):
    """Render the homepage template
    """
    if g.user['is_authenticated']:
        return redirect(url_for('lists.list'))
    return render_template('pages/homepage.html')