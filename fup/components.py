import abc
from abc import abstractmethod

from uuid import uuid4

from pynamodb.attributes import BooleanAttribute, UnicodeAttribute, MapAttribute, UTCDateTimeAttribute, NumberAttribute
from pynamodb.models import Model


import yaml


class Component(abc.ABC):

    @abstractmethod
    def init(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def status(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def teardown(self, **kwargs):
        raise NotImplementedError()


class WebComponent(Component):

    def __init__(self, **kwargs):
        pass


_attribute_lookup = {
    'string': 'UnicodeAttribute',
    'date': 'UTCDateTimeAttribute',
    'object': 'MapAttribute',
    'number': 'NumberAttribute'
}

_table_class_fmt_base = """
class {}(Model):

    class Meta:
        table_name = "{}"

{}
"""

def _rewrite_schema(schema):
    _schema = {}
    for col, type in schema.items():
        hash_key = False
        if type.endswith("*"):
            type = type.rstrip("*")
            hash_key = True
        _schema[col] = _attribute_lookup[type] + (
            "(hash_key=True)" if hash_key else "()"
        )
    return _schema

def _inject_pynamo_class(table_name: str, schema: dict):
    """
    Extremely polluting call to create a class in the global namespace
    using exec. Obviously dangerous. Don't be dumb.

    To avoid collisions, suffixes with uuid4.

    Returns a pointer to that class.
    """
    unique_tablename = table_name + str(uuid4()).replace("-", "")
    stringified_schema = ""
    for col, type in schema.items():
        stringified_schema += "\t{} = {}".format(col, type)
    print(_table_class_fmt_base.format(
        unique_tablename,
        table_name,
        stringified_schema
    ))
    return unique_tablename

class DBComponent(Component):

    def __init__(self, **kwargs):
        self.schema = kwargs.get('schema', None)
        schemafile = kwargs.get('schemafile', None)
        if self.schema is None and schemafile is None:
            raise ValueError("Must specify one of schema or schemafile.")
        if self.schema is None:
            self.schema = yaml.load(open(schemafile))

    def init(self, **kwargs):
        for table, schema in self.schema.items():
            print(table)
            print(_rewrite_schema(schema))
            print(_inject_pynamo_class(table, _rewrite_schema(schema)))
        raise NotImplementedError()

    def update(self, **kwargs):
        raise NotImplementedError()

    def status(self, **kwargs):
        raise NotImplementedError()

    def teardown(self, **kwargs):
        raise NotImplementedError()



class APIComponent(Component):

    def __init__(self, **kwargs):
        pass
