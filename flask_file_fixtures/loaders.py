"""
    flask_fixtures.loaders
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Classes for loading serialized fixtures data.

    :copyright: (c) 2015 Christopher Roach <ask.croach@gmail.com>.
    :license: MIT, see LICENSE for more details.
"""


import abc
import importlib
import logging


try:
    from dateutil.parser import parse as dtparse
except ImportError:
    print("""If you are using JSON for your fixtures, consider installing
        the dateutil library for more flexible parsing of dates and times.""")

    from datetime import datetime

    def dtparse(dt_string):
        """Returns a datetime object for the given string"""
        return datetime.strptime(dt_string, '%Y-%m-%d')

try:
    import simplejson as json
except ImportError:
    import json


try:
    import yaml
except ImportError:
    # Normally, the first argument is self, but we don't need it
    def load(_, filename):
        raise Exception("Could not load fixture '{0}'. Make sure you have PyYAML installed.".format(filename))
    yaml = type('FakeYaml', (object,), {
        'load': load
    })()


log = logging.getLogger(__name__)


class FixtureLoader(metaclass=abc.ABCMeta):
    extensions = None

    @staticmethod
    @abc.abstractmethod
    def _load_data(filename):
        pass

    @classmethod
    def load(cls, filename):
        data_dict = cls._load_data(filename)
        fixtures = list()

        # Convert the fixture dictionaries to objects
        for model_dict in data_dict:
            # Use the model name to get the model class
            class_string = model_dict['model']
            module_name, class_name = class_string.rsplit('.', 1)
            module = importlib.import_module(module_name)
            model_class = getattr(module, class_name)
            # Create the model instances
            records = model_dict['records']
            model_fixtures = [model_class(**record) for record in records]
            # Add the model instances to the fixtures list
            fixtures.extend(model_fixtures)

        return fixtures


class JSONLoader(FixtureLoader):
    extensions = ('.json', '.js')

    @staticmethod
    def _load_data(filename):
        def _datetime_parser(dct):
            for key, value in list(dct.items()):
                try:
                    dct[key] = dtparse(value)
                except (KeyError, ValueError):
                    pass
            return dct

        with open(filename) as fin:
            return json.load(fin, object_hook=_datetime_parser)


class YAMLLoader(FixtureLoader):
    extensions = ('.yaml', '.yml')

    @staticmethod
    def _load_data(filename):
        with open(filename) as fin:
            return yaml.load(fin, Loader=yaml.Loader)
