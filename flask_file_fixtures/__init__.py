import os
from .loaders import YAMLLoader, JSONLoader


class FlaskFileFixtures:
    """
    A class to load fixtures from YAML and JSON files into a Flask app's database.
    """

    def __init__(self, fixtures_dir=None, app=None, db=None):
        if app is not None:
            self.init_app(app)

        self.fixtures_dir = fixtures_dir
        self._db = db

    def init_app(self, app):
        app.extensions['flask_file_fixtures'] = self

    def load_fixtures_from_file(self, file_path):
        """Load the fixtures from a single file."""

        # If it's a YAML file, use the YAMLLoader to load the fixtures
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            fixtures = YAMLLoader.load(file_path)
        elif file_path.endswith('.json'):
            fixtures = JSONLoader.load(file_path)
        else:
            raise Exception("Could not load fixture '{0}'. Unsupported file format.".format(file_path))

        # Insert the fixtures into the database
        for fixture in fixtures:
            self._db.session.add(fixture)
        self._db.session.commit()

    def load_fixtures(self, *directories):
        """
        - Find all YAML and JSON files in the given directories.
        - Load the fixtures from each file.
        """

        # Get the full path to the fixtures directory we're loading from
        if directories is None:
            # If no directories are specified, load from the root fixtures directory
            fix_dirs = [self.fixtures_dir]
        else:
            # Otherwise, load from the specified directories, using the fixtures_dir as the root
            fix_dirs = [str(os.path.join(self.fixtures_dir, directory)) for directory in directories]

        for fix_dir in fix_dirs:
            # Test to see of ordered.txt is in the directory
            ordered_file = os.path.join(fix_dir, 'ordered.txt')
            if os.path.exists(ordered_file):
                # Load the files in the order specified in ordered.txt
                with open(ordered_file) as f:
                    ordered_files = f.read().splitlines()
            else:
                # Otherwise, load the files in alphabetical order
                ordered_files = sorted(os.listdir(fix_dir))

            for filename in ordered_files:
                # Get the file extension by splitting the filename at the last period
                extension = os.path.splitext(filename)[-1].lower()
                # Only load files with the correct extensions
                if extension in {'.yaml', '.yml', '.json', '.js'}:
                    file_path = os.path.join(fix_dir, filename)
                    self.load_fixtures_from_file(file_path)
