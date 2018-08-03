import abc
from abc import abstractmethod

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


class DBComponent(Component):

    def __init__(self, **kwargs):
        self.schema = kwargs.get('schema', None)
        schemafile = kwargs.get('schemafile', None)
        self.schema = yaml.load(open(schemafile))
        if not self.schema:
            raise ValueError("Must specify one of schema or schemafile.")

    def init(self, **kwargs):
        for table, attrs in self.schema.items():
            pass




class APIComponent(Component):

    def __init__(self, **kwargs):
        pass
