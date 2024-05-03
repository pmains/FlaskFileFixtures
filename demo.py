"""
This application demonstrates how to use the Flask-File-Fixtures extension.

# Create a clean database
flask --app demo init-db
# Load fixtures from the { FIXTURES_DIR } directory
flask --app demo load-fixtures
# Load fixtures from the { FIXTURES_DIR }/base directory
flask --app demo load-fixtures base
"""

import os
import pprint

import click

from flask import Flask
from flask_file_fixtures import FlaskFileFixtures
import dotenv

from flask_sqlalchemy import SQLAlchemy

dotenv.load_dotenv()
db = SQLAlchemy()


def create_app():
    # Check if the app already exists as an attribute of this function
    if hasattr(create_app, 'my_app'):
        return create_app.my_app

    # Create the app
    my_app = Flask(__name__)
    # Save the app as an attribute of this function
    create_app.my_app = my_app

    # Use FIXTURES_DIR from .env file
    fixtures = FlaskFileFixtures(fixtures_dir=os.getenv('FIXTURES_DIR'), db=db)
    fixtures.init_app(my_app)

    my_app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')
    my_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    my_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(my_app)

    return my_app


app = create_app()


class BaseModel(db.Model):
    __abstract__ = True

    def __repr__(self):
        return pprint.pformat(self.__dict__)


class Client(BaseModel):
    """A client who has made sales."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(255))

    # Many-to-many relationship between clients and addresses
    addresses = db.relationship('Address', backref='client', lazy=True)


class Sale(BaseModel):
    """A sale made by a client."""
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    description = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))


class Address(BaseModel):
    """An address for a client."""
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    zip_code = db.Column(db.String(255))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))

    # Many-to-many relationship between clients and addresses
    clients = db.relationship('Client', backref='address', lazy=True)


@app.cli.command("init-db")
def init_db():
    """Create all tables in the database."""
    # Start by dropping all tables
    db.drop_all()
    db.create_all()


@app.cli.command("load-fixtures")
@click.argument("dirs", nargs=-1)
def load_fixtures(dirs):
    """Load fixtures into the database."""
    fixtures = app.extensions['flask_file_fixtures']
    fixtures.load_fixtures(*dirs)


@app.route('/')
def hello():
    """List all sales and customers"""
    sales = Sale.query.all()
    clients = Client.query.all()
    data_str = pprint.pformat({
        'sales': sales,
        'clients': clients,
    }, indent=4, width=1)

    return f"<pre>{data_str}</pre>"


if __name__ == '__main__':
    app.run(debug=True)
