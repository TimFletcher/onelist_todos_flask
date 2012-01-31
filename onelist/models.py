import os
from flask import g

class BaseModel(object):

    def __init__(self, db, table):
        self.db = db
        self.params = {}
        self.params['table'] = table


    def get(self, **kwargs):
        """Returns a single object from the table::

        :param kwargs: the column/value pairings that should be used for the
                       where lookup.
        """
        # Dictionary keys and values are listed in an arbitary order so it's fine
        # to grab keys and values separately.
        # http://docs.python.org/release/2.6.4/library/stdtypes.html#dict.items
        self.params['where'] = ' and '.join(['{0} = %s'.format(c) for c in kwargs.keys()])
        sql = 'SELECT * from {table} WHERE {where}'.format(**self.params)
        return self.db.get(sql, *kwargs.values())


    def create(self, **kwargs):
        """Creates an object in the table and returns it::

        :param kwargs: the column/value mappings for the data.
        """
        columns = kwargs.keys()
        self.params['columns'] = ", ".join(columns)
        self.params['values'] = ", ".join("%s" for v in columns)
        sql = "INSERT INTO {table} ({columns}) VALUES ({values})".format(**self.params)
        id = self.db.execute(sql, *kwargs.values())
        return self.get(id=id)


    def update(self, columns, where):
        """Update an object in the table
        
        :param columns: the column/value mappings for the columns to be updated.
        :param where: the column/value pairings that should be used for the
                      where lookup.
        """
        self.params['cols_vals'] = ", ".join(['{0} = %s'.format(c) for c in columns.keys()])
        self.params['where'] = ' and '.join(['{0} = %s'.format(c) for c in where.keys()])
        values = columns.values() + where.values()
        sql = "UPDATE {table} SET {cols_vals} WHERE {where}".format(**self.params)
        self.db.execute(sql, *values)


    def delete(self, **kwargs):
        """Deletes a single object from the table::

        :param kwargs: the column/value pairings that should be used for the
                       where lookup.
        """
        self.params['where'] = ' and '.join(['{0} = %s'.format(c) for c in kwargs.keys()])
        sql = 'DELETE FROM {table} WHERE {where} LIMIT 1'.format(**self.params)
        return self.db.execute(sql, *kwargs.values())


    def all(self):
        """Returns all objects from the table::
        """
        sql = 'SELECT * from {table}'.format(**self.params)
        return self.db.query(sql)


    def select(self):
        pass