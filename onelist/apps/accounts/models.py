from werkzeug import generate_password_hash, check_password_hash
from flask import g, current_app
from onelist.models import BaseModel

class UserModel(BaseModel):

    def create(self, email, password):
        """Create and return a new user.
        """
        # Normalise Email Address
        try:
            email_name, domain_part = email.strip().split('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])
        kwargs = {'email': email,
                  'password': generate_password_hash(password)}
        return super(UserModel, self).create(**kwargs)


    def authenticate(self, email, password):
        """Validate that a user exists with the supplied credentials
        """
        user = self.get(email=email)
        if user:
            if check_password_hash(user['password'], password):
                return user
        return False


    def get_user_by_listitem_id(self, listitem_id):
        sql = """SELECT lists_list.user_id
                 FROM lists_listitem
                 INNER JOIN lists_list
                 ON lists_listitem.list_id = lists_list.id
                 WHERE lists_listitem.id = %s;"""
        try:
            user_id = self.db.get(sql, listitem_id).user_id
            return self.get(id=user_id)
        except AttributeError, e:
            current_app.logger.error('No user was found by get_user_by_listitem_id. SQL: listitem_id was {0}'.format(listitem_id))
            # How do we sometimes get here?
            pass


    def change_password(self, password, user):
        self.update(columns={'password': generate_password_hash(password)},
                             where={'id': user.id})