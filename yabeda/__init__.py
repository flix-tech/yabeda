"""Appfactory to create an app from this module."""
import logging

from flask import Flask
from flasgger import Swagger

from yabeda import __main__
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)


def create_app(test_config=None):
    """Return a Flask app with the blueprints and config from this module."""
    app = Flask(__name__)
    swagger = Swagger()

    if test_config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.update(test_config)

    swagger.init_app(app)

    app.register_blueprint(__main__.root)

    return app
