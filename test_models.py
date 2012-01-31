import os
import unittest

from flask import request, g

from onelist.application import create_app
from onelist.config import TestingConfig
from onelist.config import ROOT
from onelist.apps.accounts.models import UserModel
from onelist.apps.lists.models import ListModel, ListItemModel


SQL = [
    open(os.path.join(ROOT, 'schema.sql'), 'r').read(),
    open(os.path.join(ROOT, 'fixtures.sql'), 'r').read()
]


def process_sql(sql):
    """Take in a raw SQL file object and yield each individual SQL statement.
    """
    statements = [s for s in sql.strip().split(";") if s]
    for s in statements:
        yield "{0};".format(s)


class OneListTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        self.app.preprocess_request()
        self.user = "{'first_name': u'Tim', 'last_name': u'Fletcher', " \
        "'is_active': '1', 'email': u'test@test.com', 'password': " \
        "u'sha1$huj9heME$8653756aaed11fdbfce799d27644866efa291efd', 'id': 1L}"
        self.all_items = "[{'text': u'Take cat to vet', 'id': 1L, 'complete': 0, 'list_id': 1L}, " \
        "{'text': u'Clean house', 'id': 2L, 'complete': 0, 'list_id': 1L}, " \
        "{'text': u'Buy birthday card for sis', 'id': 3L, 'complete': 0, 'list_id': 1L}, " \
        "{'text': u'Go to gym', 'id': 4L, 'complete': 0, 'list_id': 1L}, " \
        "{'text': u'Take bike to shop', 'id': 5L, 'complete': 0, 'list_id': 2L}, " \
        "{'text': u'Buy flowers', 'id': 6L, 'complete': 0, 'list_id': 2L}, " \
        "{'text': u'Take dog out for a walk', 'id': 7L, 'complete': 0, 'list_id': 2L}, " \
        "{'text': u'Fix sink', 'id': 8L, 'complete': 0, 'list_id': 2L}]"
        for sql in SQL:
            for statement in process_sql(sql):
                g.db.execute(statement)


    def tearDown(self):
        """Roll back any database changes and enable autocommit. (If we could
        get it to work)
        """
        # g.db.execute('ROLLBACK;')
        # g.db.set_autocommit(True)
        self.app.process_response(self.app.response_class())
        self.ctx.pop()

    # -----------------------
    # --- DAL Model Tests ---
    # -----------------------

    def test_dal_get(self):
        # By a single field
        user = g.User.get(email="test@test.com")
        self.assertEqual(str(user), self.user)
        
        # By multiple fields
        user = g.User.get(email="test@test.com", first_name="Tim", last_name="Fletcher", id=1)
        self.assertEqual(str(user), self.user)


    def test_dal_create(self):
        g.ListItem.create(list_id=1, text="This is a new list item")
        list_item = g.ListItem.get(id=9)
        expected_list_item = {'text': u'This is a new list item', 'id': 9L, 'complete': 0, 'list_id': 1L}
        self.assertEqual(list_item, expected_list_item)


    def test_dal_update(self):
        # Single column
        user = g.User.get(email="test@test.com")
        g.User.update(columns={'first_name': 'Mai-Linh'}, where={'id': user.id})
        new_user = g.User.get(email="test@test.com")
        self.assertNotEqual(user, new_user)

        # Multiple column
        user = g.User.get(email='test@test.com')
        g.User.update(columns={'first_name': 'Mai-Linh',
                               'last_name': 'Huynh',
                               'is_active': 0},
                      where={'id': user.id})
        new_user = g.User.get(email="test@test.com")
        self.assertNotEqual(user, new_user)


    def test_dal_delete_single_column(self):
        user = g.User.get(email='test@test.com')
        g.User.delete(email='test@test.com')
        new_user = g.User.get(email='test@test.com')
        self.assertNotEqual(user, new_user)
        self.assertEqual(new_user, None)


    def test_dal_delete_multiple_column(self):
        user = g.User.get(email='test@test.com')
        g.User.delete(email='test@test.com', first_name='Tim', last_name='Fletcher')
        new_user = g.User.get(email="test@test.com")
        self.assertNotEqual(user, new_user)
        self.assertEqual(new_user, None)


    def test_dal_all(self):
        all_items = g.ListItem.all()
        self.assertEqual(str(all_items), self.all_items)
        self.assertEqual(len(all_items), 8)

    # --------------------
    # --- AccountModel ---
    # --------------------

    def test_accounts_model_create(self):
        user = g.User.create(email="new@user.com", password="admin")
        self.assertEqual(user.email, 'new@user.com')


    def test_accounts_model_authenticate(self):
        # Credentials are correct
        user = g.User.authenticate(email="test@test.com", password="admin")
        self.assertEqual(1, user.id)
        # Password is incorrect
        user = g.User.authenticate(email="test@test.com", password="wrong")
        self.assertFalse(user)
        # Email doesn't exist
        user = g.User.authenticate(email="foo@bar.com", password="admin")
        self.assertFalse(user)


    def test_accounts_model_get_user_by_listitem_id(self):
        user = g.User.get_user_by_listitem_id(1)
        self.assertEqual(user.email, 'test@test.com')


    def test_change_password(self):
        user = g.User.authenticate(email="test@test.com", password="admin")
        self.assertEqual(1, user.id)
        g.User.change_password('floopy', user)
        new_user = g.User.authenticate(email="test@test.com", password="floopy")
        self.assertEqual(1, new_user.id)

    # -----------------
    # --- ListModel ---
    # -----------------

    def test_create(self):
        user = g.User.create(email="foo@bar.com", password="crundle")
        g.List.create(user)
        self.assertEqual(3, user.id)

    # ---------------------
    # --- ListItemModel ---
    # ---------------------

    def test_get_for_user(self):
        user = g.User.get(email='test@test.com')
        all_items_count = len(g.ListItem.all())
        items = g.ListItem.get_for_user(user)
        count = sum(1 for i in items)
        self.assertEqual(4, count)
        self.assertNotEqual(all_items_count, count)

    def test_toggle_complete(self):
        original_list_item = g.ListItem.get(id=1)
        g.ListItem.toggle_complete(id=original_list_item.id)
        updated_list_item = g.ListItem.get(id=1)
        self.assertNotEqual(original_list_item.complete, updated_list_item.complete)


if __name__ == '__main__':
    unittest.main()