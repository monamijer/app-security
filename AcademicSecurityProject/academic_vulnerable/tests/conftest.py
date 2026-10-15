import os
import sys
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(HERE)
sys.path.insert(0, APP_DIR)


@pytest.fixture
def app():
    os.environ.setdefault("SECRET_KEY", "test-secret")
    from app import create_app
    from models import db
    app = create_app()
    app.config.update(TESTING=True,
                      SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()