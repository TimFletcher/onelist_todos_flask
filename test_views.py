import os
import unittest

from flask import request, g, url_for, session

from onelist.application import create_app
from onelist.config import TestingConfig
from onelist.config import ROOT

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

    # ---------------------------------
    # --- Tests for accounts module ---
    # ---------------------------------

    def login(self, email, password):
        return self.client.post(url_for('accounts.login'),
                                data=dict(email=email,
                                          password=password),
                                follow_redirects=True)


    def logout(self):
        return self.client.get(url_for('accounts.logout'), follow_redirects=True)


    def register(self, email, password, confirm):
        return self.client.post(url_for('accounts.register'),
                                data=dict(email=email,
                                          password=password,
                                          confirm=confirm),
                                follow_redirects=True)


    def test_login(self):
        # Page loads
        rv = self.client.get(url_for('accounts.login'))
        self.assertEqual(rv.status_code, 200)

        # Page loads when logging in and it's the right page.
        rv = self.login('test@test.com', 'admin')
        self.assertEqual(rv.status_code, 200)
        assert 'test@test.com' in rv.data

        # Incorrect credentials prevents login
        self.logout()
        rv = self.login('test@test.com', 'wrong')
        assert "Incorrect email and/or password" in rv.data


    def test_logout(self):
        self.login('test@test.com', 'admin')
        rv = self.logout()
        self.assertEqual(rv.status_code, 200)
        assert "successfully logged out." in rv.data


    def test_register_correct(self):
        rv = self.register(email='new@registration.com',
                           password='shizzle',
                           confirm='shizzle')
        self.assertEqual(rv.status_code, 200)
        assert "created your account" in rv.data


    def test_register_incorrect(self):
        # Email already registered
        rv = self.register(email='test@test.com',
                           password='admin',
                           confirm='admin')
        self.assertEqual(rv.status_code, 200)
        assert "Email already in use" in rv.data

        # Password confirm not equal to password
        rv = self.register(email='test@test.com',
                           password='admin',
                           confirm='wrong')
        self.assertEqual(rv.status_code, 200)
        assert "Passwords must match" in rv.data


    def test_password_change(self):
        new_password = 'rumpus'

        # Page loads
        self.login('test@test.com', 'admin')
        rv = self.client.get(url_for('accounts.password_change'))

        # Password can be changed
        self.assertEqual(rv.status_code, 200)
        rv = self.client.post(url_for('accounts.password_change'),
                              data=dict(password=new_password,
                                        confirm=new_password),
                              follow_redirects=True)
        assert "Your password was successfully changed" in rv.data

        # New password allows login.
        self.logout()
        rv = self.login('test@test.com', new_password)
        assert 'test@test.com' in rv.data

        # Incorrect password confirmation doesn't validate
        rv = self.client.post(url_for('accounts.password_change'),
                              data=dict(password='password',
                                        confirm='wrong'))
        assert "Passwords must match" in rv.data


    def test_password_reset_request(self):
        # Page loads if logged out
        rv = self.client.get(url_for('accounts.password_reset_request'))
        self.assertEqual(rv.status_code, 200)

        # Access denied if logged in
        self.login('test@test.com', 'admin')
        rv = self.client.get(url_for('accounts.password_reset_request'))
        self.assertEqual(rv.status_code, 403)
        assert "not allowed to access" in rv.data
        self.logout()

        # Can request reset
        rv = self.client.post(url_for('accounts.password_reset_request'),
                              data=dict(email='test@test.com'),
                              follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        assert "Password Reset Request Complete" in rv.data

        # Invalid email throws validation error
        rv = self.client.post(url_for('accounts.password_reset_request'),
                              data=dict(email='invalid@email.com'),
                              follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        assert "Email address not registered." in rv.data


    def test_password_reset_request_complete(self):
        # Access denied if logged in
        self.login('test@test.com', 'admin')
        rv = self.client.get(url_for('accounts.password_reset_request_complete'))
        self.assertEqual(rv.status_code, 403)
        assert "not allowed to access" in rv.data


    def test_password_reset_request_confirm(self):
        # Show error if token is invalid
        rv = self.client.get(url_for('accounts.password_reset_request_confirm',
                                     token='wrong'),
                             follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        assert "The password reset link was invalid" in rv.data

        # Deny access if logged in
        self.login('test@test.com', 'admin')
        rv = self.client.get(url_for('accounts.password_reset_request_confirm',
                                     token='wrong'),
                             follow_redirects=True)
        self.assertEqual(rv.status_code, 403)
        self.logout()

        # Correct token allows login
        from onelist.apps.accounts.tokens import token_generator
        user = g.User.get(email='test@test.com')
        token = token_generator.make_token(user)
        rv = self.client.get(url_for('accounts.password_reset_request_confirm',
                                     token=token),
                             follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        assert 'test@test.com' in rv.data

        # ------------------------------
        # --- Tests for pages module ---
        # ------------------------------

    def test_homepage(self):
        # Page loads if logged out
        rv = self.client.get(url_for('pages.homepage'))
        self.assertEqual(rv.status_code, 200)
        assert 'OneList is a really simple todo list application' in rv.data

        # Redirect to list page if logged in
        self.login('test@test.com', 'admin')
        rv = self.client.get(url_for('pages.homepage'),
                             follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        assert '<body class="lists" id="list">' in rv.data

        # ------------------------------
        # --- Tests for lists module ---
        # ------------------------------

    def test_list(self):
        self.login('test@test.com', 'admin')
        rv = self.client.get(url_for('lists.list'))
        self.assertEqual(rv.status_code, 200)


    def test_add_item(self):
        self.login('test@test.com', 'admin')
        user = g.User.get(email='test@test.com')
        before_item_count = len(list(g.ListItem.get_for_user(user)))
        rv = self.client.post(url_for('lists.add_item'),
                              data={'text-add': 'New list item'})
        after_item_count = len(list(g.ListItem.get_for_user(user)))
        self.assertEqual(rv.status_code, 200)
        assert "9" in rv.data
        assert "New list item" in rv.data
        self.assertNotEqual(before_item_count, after_item_count)


    def test_add_item_via_hash(self):
        from onelist.apps.lists.helpers import generate_hash
        user = g.User.get(email='test@test.com')
        hash = generate_hash('test@test.com')

        # Page loads
        rv = self.client.get(url_for('lists.add_item_via_hash', hash=hash))
        self.assertEqual(rv.status_code, 200)

        # Can add a new item
        before_item_count = len(list(g.ListItem.get_for_user(user)))
        rv = self.client.post(url_for('lists.add_item_via_hash',
                                      hash=hash),
                              data={'text-add': 'New list item'},
                              follow_redirects=True)
        after_item_count = len(list(g.ListItem.get_for_user(user)))
        self.assertEqual(rv.status_code, 200)
        assert "by_hash" in rv.data
        self.assertNotEqual(before_item_count, after_item_count)
        assert "Sorry, an error has occurred" not in rv.data


    def test_edit_item(self):
        # Can update an item
        self.login('test@test.com', 'admin')
        before_item = g.ListItem.get(id=1)
        rv = self.client.post(url_for('lists.edit_item', item_id=1),
                              data={'text-1': 'New list item'})
        after_item = g.ListItem.get(id=1)
        self.assertEqual(rv.status_code, 200)
        self.assertNotEqual(before_item, after_item)
        self.assertEqual(after_item.text, 'New list item')

        # If list item doesn't exist, don't throw an error
        rv = self.client.post(url_for('lists.edit_item', item_id=10),
                              data={'text-10': 'New list item'})
        self.assertEqual(rv.status_code, 200)

        # Updating to a blank item deletes the item
        rv = self.client.post(url_for('lists.edit_item', item_id=2),
                              data={'text-2': ''})
        after_item = g.ListItem.get(id=2)
        self.assertEqual(after_item, None)

        # Only allow owner to edit their own items
        rv = self.client.post(url_for('lists.edit_item', item_id=5),
                              data=dict(text='New list item'))
        self.assertEqual(rv.status_code, 403)


    def test_delete_item(self):
        # Can delete an item
        self.login('test@test.com', 'admin')
        before_item = g.ListItem.get(id=1)
        rv = self.client.post(url_for('lists.delete_item', item_id=1))
        self.assertEqual(rv.status_code, 200)
        after_item = g.ListItem.get(id=1)
        self.assertEqual(after_item, None)
        
        # If list item doesn't exist, don't throw an error
        rv = self.client.post(url_for('lists.delete_item', item_id=10))
        self.assertEqual(rv.status_code, 200)

        # Only allow owner to delete their own items
        rv = self.client.post(url_for('lists.delete_item', item_id=5))
        self.assertEqual(rv.status_code, 403)


if __name__ == '__main__':
    unittest.main()