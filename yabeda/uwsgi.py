"""Helper module for uwsgi.

uwsgi expects a callable `app` in the module it is pointed to.

"""
from yabeda import create_app

app = create_app()

