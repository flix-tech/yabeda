from yabeda import create_app


def test_config():
    assert not create_app().testing
    config = {
        # the test
        'TESTING': True
    }
    assert create_app(config).testing
