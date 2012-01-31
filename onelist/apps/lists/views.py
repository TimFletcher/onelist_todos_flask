from flask import Module, g, render_template, flash, request, redirect, session, \
        url_for, make_response, jsonify, current_app, abort
from onelist.apps.accounts.helpers import login_required
from onelist.apps.accounts.tokens import token_generator

module = Module(__name__, 'lists')

@module.route('/')
@login_required
def list():
    """Show an authenticated user their list
    """
    items = g.ListItem.get_for_user(g.user)
    return render_template('lists/list.html', **locals())


@module.route('/add/', methods=['POST'])
@login_required
def add_item():
    """Post a new item to a user's list via their list page. This is an AJAX
    method.
    """
    if current_app.debug: # For testing slow requests.
        import time
        time.sleep(0.5)
    try:
        text = request.form.get('text-add', None)
        if text:
            list_obj = g.List.get(user_id=g.user.id)
            item = g.ListItem.create(list_id=list_obj.id, text=text)
            return jsonify(insert_id=item.id, text=text)
    except Exception, e:
        current_app.logger.error("There was an error whilst adding a list item.")
        abort(500)


@module.route('/add/<hash>/', methods=['GET', 'POST'])
def add_item_via_hash(hash):
    """Post a new item to an unauthenticated user's list via the api. The key
    parameter is generated based on a user's account email. The key will be
    sufficiently unique such that only the correct user will be able to generate it.
    """
    if current_app.debug: # For testing slow requests.
        import time
        time.sleep(0.5)
    if request.method == 'POST':
        text = request.form.get('text-add', None)
        if text:
            try:
                list_obj = g.List.get(hash=hash)
                item = g.ListItem.create(list_id=list_obj.id, text=text)
                return jsonify(insert_id=item.id, text=text, by_hash=True)
            except Exception, e:
                current_app.logger.error('There was an error adding an item via '
                                         'hash: {0}: {1}'.format(hash, e))
                abort(500)
    return render_template('lists/add.html', **locals())


@module.route('/edit/<item_id>/', methods=['POST'])
@login_required
def edit_item(item_id):
    """Edit an item on a user's list via their list page. This is an AJAX method.
    """
    text = request.form.get('text-{0}'.format(item_id), '')
    # Sanity check that item exists - it could have been deleted in another tab
    list_item = g.ListItem.get(id=item_id)
    if not list_item:
        return delete_item(item_id)
    # If item does exist but it's blank, delete it.
    if list_item and not text:
        return delete_item(item_id)
    user = g.User.get_user_by_listitem_id(item_id)
    if user.id == g.user.id:
        try:
            g.ListItem.update(columns={'text': text}, where={'id': item_id})
            return jsonify(id_updated="item-{0}".format(item_id))
        except Exception, e:
            current_app.logger.error('There was an error editing item {0}'.format(item_id))
            abort(500)
    abort(403)


@module.route('/delete/<item_id>/', methods=['POST'])
@login_required
def delete_item(item_id):
    """ Delete an item on a user's list via their list page. This is an AJAX method.
    """
    # Sanity check that item exists. If it doesn't, simply remove it from
    # the DOM as for a normal delete
    if not g.ListItem.get(id=item_id):
        return jsonify(id_to_remove="item-{0}".format(item_id))
    user = g.User.get_user_by_listitem_id(item_id)
    if user.id == g.user.id:
        try:
            g.ListItem.delete(id=item_id)
            return jsonify(id_to_remove="item-{0}".format(item_id))
        except Exception, e:
            current_app.logger.error('There was an error deleting item {0}'.format(item_id))
            abort(500)
    abort(403)
    
@module.route('/checkoff/<item_id>/', methods=['POST'])
@login_required
def checkoff_item(item_id):
    """ Toggle the done status of an item on a user's list via their list page.
    This is an AJAX method.
    """
    # Sanity check that item exists. If it doesn't, simply remove it from
    # the DOM
    if not g.ListItem.get(id=item_id):
        return jsonify(id_to_remove="item-{0}".format(item_id))
    user = g.User.get_user_by_listitem_id(item_id)
    if user.id == g.user.id:
        try:
            g.ListItem.toggle_complete(id=item_id)
            return jsonify(id_to_toggle_checkoff='item-{0}'.format(item_id))
        except Exception, e:
            current_app.logger.error('There was an error checking off item '
                                     '{0}'.format(item_id))
            abort(500)
    abort(403)