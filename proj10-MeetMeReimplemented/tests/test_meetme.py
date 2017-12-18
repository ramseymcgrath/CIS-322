# -*- coding: utf-8 -*-
"""
    MeetMe Tests
    ~~~~~~~~~~~~~~

    Tests the MeetMe application.

    :copyright: (c) 2017 ramsey McGrath
    :Based off of Flask's Minitwit Example
    :license: BSD, see LICENSE for more details.

    These are largly broken, we need to reimplement now that we're using googles auth
"""
import os
import tempfile
import httplib2
import googleapiclient
import flask
import meetme


@pytest.fixture
def client():
    db_fd, meetme.app.config['DATABASE'] = tempfile.mkstemp()
    client = meetme.app.test_client()
    with meetme.app.app_context():
        flask.current_app()
    yield client
    os.close(db_fd)
    os.unlink(meetme.app.config['DATABASE'])


def register(client, username, password, password2=None, email=None):
    """Helper function to register a user"""
    if email is None:
        email = username + '@example.com'
    return client.post('/register', data={
        'username':     username,
        'password':     password,
    }, follow_redirects=True)


def login(client, username, password):
    """Helper function to login"""
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


def register_and_login(client, username, password):
    """Registers and logs in in one go"""
    register(client, username, password)
    return login(client, username, password)


def logout(client):
    """Helper function to logout"""
    return client.get('/logout', follow_redirects=True)

def test_register(client):
    """Make sure registering works"""
    rv = register(client, 'user1')
    assert b'Success!' 



def test_login_logout(client):
    """Make sure logging in and logging out works"""
    rv = register_and_login(client, 'user1', 'default')
    assert b'You were logged in' in rv.data
    rv = logout(client)
    assert b'You were logged out' in rv.data
    rv = login(client, 'user1', 'wrongpassword')
    assert b'Invalid password' in rv.data
    rv = login(client, 'user2', 'wrongpassword')
    assert b'Invalid username' in rv.data


def test_message_recording(client):
    """Check if adding messages works"""
    register_and_login(client, 'foo', 'default')
    add_new_meeting('1')
    add_new_meeting('2')
    rv = client.get('/')
    assert b'1' in rv.data
    assert b'2' in rv.data


def test_timelines(client):
    """Make sure that timelines work"""
    register_and_login(client, 'foo', 'default')
    add_new_meeting('42')
    logout(client)
    register_and_login(client, 'foo', 'default')
    assert b'42' in rv.data
