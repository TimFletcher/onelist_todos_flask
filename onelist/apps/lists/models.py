from onelist.apps.lists.helpers import generate_hash
from onelist.models import BaseModel
from flask import g

class ListModel(BaseModel):

    def create(self, user):
        kwargs = {'user_id': user.id,
                  'hash': generate_hash(user.email)}
        return super(ListModel, self).create(**kwargs)


class ListItemModel(BaseModel):

    def get_for_user(self, user):
        sql = """SELECT lists_listitem.id, lists_listitem.text, lists_listitem.complete
                 FROM lists_listitem
                 INNER JOIN lists_list
                 ON lists_listitem.list_id = lists_list.id
                 WHERE user_id = %s;"""
        return self.db.iter(sql, user.id)


    def toggle_complete(self, **kwargs):
        """Toggle the complete column for the list item

        :param kwargs: the column/value pairings that should be used for the
                       where lookup.
        """
        self.params['where'] = ' and '.join(['{0} = %s'.format(c) for c in kwargs.keys()])
        sql = 'UPDATE {table} SET complete = 1 XOR complete WHERE {where}'.format(**self.params)
        return self.db.execute(sql, *kwargs.values())