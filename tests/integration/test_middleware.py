"""Integration tests."""

import pytest
from yabeda import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_ping(client):
    response = client.get('/ping')
    assert response.data == 'pong'.encode()
    assert response.status_code == 200
