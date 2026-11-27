import pytest
from app import create_app
from extensions import db

class TestConfig:
    TESTING=True
    SECRET_KEY='test-secret'
    SQLALCHEMY_DATABASE_URI='sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    WTF_CSRF_ENABLED=False
    RATELIMIT_ENABLED=False

@pytest.fixture
def client():
    app=create_app(TestConfig)
    with app.app_context(): db.create_all()
    with app.test_client() as client: yield client
    with app.app_context(): db.drop_all()

def test_register_login_and_private_route(client):
    r=client.post('/register',data={'full_name':'Test Person','user_id':'testuser','email':'test@example.com','password':'StrongPassword123','confirm_password':'StrongPassword123'})
    assert r.status_code==200
    r=client.post('/login',data={'identity':'testuser','password':'StrongPassword123'})
    assert r.status_code==302
    assert client.get('/dashboard').status_code==200

def test_duplicate_registration(client):
    data={'full_name':'Test','user_id':'testuser','email':'test@example.com','password':'StrongPassword123','confirm_password':'StrongPassword123'}
    assert client.post('/register',data=data).status_code==200
    r=client.post('/register',data={**data,'email':'other@example.com'})
    assert b'already registered' in r.data

def test_task_route_requires_login(client):
    assert client.get('/tasks/').status_code==302
