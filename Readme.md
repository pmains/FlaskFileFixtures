# Installation
python setup.py sdist bdist_wheel
pip install .

# Usage
When creating your Flask application, include the following code:

```
fixtures = FlaskFileFixtures(fixtures_dir=os.getenv('FIXTURES_DIR'), db=db)
fixtures.init_app(my_app)
```

To register the load-fixtures command, include the following code or something similar:

```
@app.cli.command("load-fixtures")
@click.argument("dirs", nargs=-1)
def load_fixtures(dirs):
    """Load fixtures into the database."""
    fixtures = app.extensions['flask_file_fixtures']
    fixtures.load_fixtures(*dirs)
```

- 'db' is a reference to your SQLAlchemy database object.
- 'FIXTURES_DIR' is an environment variable that should be set to the directory containing your fixtures.

# Fixtures

Your fixtures should be stored in the directory specified by the 'FIXTURES_DIR' environment variable. The fixtures
should be stored in YAML or JSON format. For example:

```
# fixtures/users.yaml
- model: project.models.User
  records:
    - username: my_username
      email: user@example.com
      password: my_password
      related_id: 1
    - username: my_other_username
      email: other@example.com
      password: my_other_password
      related_id: 2
      ... 
```

# Order of installation
If the order of installation is important, you can specify the order in the order.txt file. For example:

```
# fixtures/dir/order.txt
roles.yaml
users.yaml
permissions.yaml
```

This guarantees that roles will be installed before users and users will be installed before permissions.