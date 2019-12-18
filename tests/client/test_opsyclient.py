import json
import httpretty
import pytest
from bravado.exception import HTTPUnauthorized, HTTPForbidden
from opsyclient.client import OpsyClient


@httpretty.activate
def test_init():
    """Make sure the client initializes correctly"""
    httpretty.register_uri(
        httpretty.GET, 'http://localhost/docs/swagger.json',
        body=open('tests/data/swagger.json', 'r').read(),
        content_type='application/json')
    opsy = OpsyClient(url='http://localhost/')
    assert opsy.authenticated is False
    assert dir(opsy).sort() == ['authenticate', 'authenticated', 'get_model',
                                'groups', 'hosts', 'login', 'http_client',
                                'swagger_spec', 'url', 'zones'].sort()


@httpretty.activate
def test_auth_success():
    """Test that we can log in with the client."""

    def login_post_callback(request, uri, response_headers):
        """Make sure the request includes all the creds"""
        request_body = json.loads(request.body.decode("utf-8"))
        assert request_body['user_name'] == 'admin'
        assert request_body['password'] == 'password'
        assert request_body['force_renew'] is False
        response_headers = {'Content-Type': 'application/json'}
        response_body = open('tests/data/login_success.json', 'r').read()
        return [200, response_headers, response_body]

    def login_get_callback(request, uri, response_headers):
        """Make sure the request includes the auth token"""
        auth_token = json.loads(
            open('tests/data/login_success.json', 'r').read())['token']
        assert request.headers.get('X-AUTH-TOKEN') == auth_token
        response_headers = {'Content-Type': 'application/json'}
        response_body = open('tests/data/login_success.json', 'r').read()
        return [200, response_headers, response_body]

    httpretty.register_uri(
        httpretty.GET, 'http://localhost/docs/swagger.json',
        body=open('tests/data/swagger.json', 'r').read(),
        content_type='application/json')
    httpretty.register_uri(
        httpretty.POST, 'http://localhost/api/v1/login/',
        body=login_post_callback)
    httpretty.register_uri(
        httpretty.GET, 'http://localhost/api/v1/login/',
        body=login_get_callback)
    opsy = OpsyClient(url='http://localhost/')
    assert opsy.authenticated is False
    opsy.authenticate('admin', 'password')
    assert opsy.authenticated is True
    assert opsy.login.show_login().response().result.user_name == 'admin'
    opsy = OpsyClient(
        url='http://localhost/', user_name='admin', password='password')
    assert opsy.authenticated is True
    assert opsy.login.show_login().response().result.user_name == 'admin'


@httpretty.activate
def test_auth_success_force_renew():
    """Test that we can log in with the client using force renew."""

    def login_post_callback(request, uri, response_headers):
        """Make sure the request includes all the creds"""
        request_body = json.loads(request.body.decode("utf-8"))
        assert request_body['user_name'] == 'admin'
        assert request_body['password'] == 'password'
        assert request_body['force_renew'] is True
        response_headers = {'Content-Type': 'application/json'}
        response_body = open('tests/data/login_success.json', 'r').read()
        return [200, response_headers, response_body]

    def login_get_callback(request, uri, response_headers):
        """Make sure the request includes the auth token"""
        auth_token = json.loads(
            open('tests/data/login_success.json', 'r').read())['token']
        assert request.headers.get('X-AUTH-TOKEN') == auth_token
        response_headers = {'Content-Type': 'application/json'}
        response_body = open('tests/data/login_success.json', 'r').read()
        return [200, response_headers, response_body]

    httpretty.register_uri(
        httpretty.GET, 'http://localhost/docs/swagger.json',
        body=open('tests/data/swagger.json', 'r').read(),
        content_type='application/json')
    httpretty.register_uri(
        httpretty.POST, 'http://localhost/api/v1/login/',
        body=login_post_callback)
    httpretty.register_uri(
        httpretty.GET, 'http://localhost/api/v1/login/',
        body=login_get_callback)
    opsy = OpsyClient(url='http://localhost/')
    assert opsy.authenticated is False
    opsy.authenticate('admin', 'password', force_renew=True)
    assert opsy.authenticated is True
    assert opsy.login.show_login().response().result.user_name == 'admin'
    opsy = OpsyClient(
        url='http://localhost/', user_name='admin', password='password',
        force_renew=True)
    assert opsy.authenticated is True
    assert opsy.login.show_login().response().result.user_name == 'admin'


@httpretty.activate
def test_auth_success_no_models():
    """Test that we can log in with the client."""

    def login_post_callback(request, uri, response_headers):
        """Make sure the request includes all the creds"""
        request_body = json.loads(request.body.decode("utf-8"))
        assert request_body['user_name'] == 'admin'
        assert request_body['password'] == 'password'
        assert request_body['force_renew'] is False
        response_headers = {'Content-Type': 'application/json'}
        response_body = open('tests/data/login_success.json', 'r').read()
        return [200, response_headers, response_body]

    def login_get_callback(request, uri, response_headers):
        """Make sure the request includes the auth token"""
        auth_token = json.loads(
            open('tests/data/login_success.json', 'r').read())['token']
        assert request.headers.get('X-AUTH-TOKEN') == auth_token
        response_headers = {'Content-Type': 'application/json'}
        response_body = open('tests/data/login_success.json', 'r').read()
        return [200, response_headers, response_body]

    httpretty.register_uri(
        httpretty.GET, 'http://localhost/docs/swagger.json',
        body=open('tests/data/swagger.json', 'r').read(),
        content_type='application/json')
    httpretty.register_uri(
        httpretty.POST, 'http://localhost/api/v1/login/',
        body=login_post_callback)
    httpretty.register_uri(
        httpretty.GET, 'http://localhost/api/v1/login/',
        body=login_get_callback)
    opsy = OpsyClient(url='http://localhost/', use_models=False)
    assert opsy.authenticated is False
    opsy.authenticate('admin', 'password')
    assert opsy.authenticated is True
    assert opsy.login.show_login().response().result['user_name'] == 'admin'
    opsy = OpsyClient(
        url='http://localhost/', user_name='admin', password='password',
        use_models=False)
    assert opsy.authenticated is True
    assert opsy.login.show_login().response().result['user_name'] == 'admin'


@httpretty.activate
def test_auth_failed():
    """Test that we throw an exception when login fails."""

    httpretty.register_uri(
        httpretty.GET, 'http://localhost/docs/swagger.json',
        body=open('tests/data/swagger.json', 'r').read(),
        content_type='application/json')
    httpretty.register_uri(
        httpretty.POST, 'http://localhost/api/v1/login/',
        body=open('tests/data/login_failed.json', 'r').read(),
        content_type='text/html', status=401)
    httpretty.register_uri(
        httpretty.GET, 'http://localhost/api/v1/login/',
        body=open('tests/data/login_failed.json', 'r').read(),
        content_type='text/html', status=403)
    opsy = OpsyClient(url='http://localhost/')
    assert opsy.authenticated is False
    with pytest.raises(HTTPUnauthorized):
        opsy.authenticate('admin', 'badpassword')
    assert opsy.authenticated is False
    with pytest.raises(HTTPUnauthorized):
        opsy = OpsyClient(
            url='http://localhost/', user_name='admin', password='password')
    with pytest.raises(HTTPForbidden):
        opsy.login.show_login().response().result
