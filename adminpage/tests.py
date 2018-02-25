from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.test import TestCase
from wechat.models import User, Activity
from django.contrib import auth
import adminpage.urls, json
from codex.baseerror import InputError
from unittest.mock import *

class LoginTest(TestCase):
    fixtures = ['admin.json']

    def test_a_login(self):
        response = self.client.get('/a/login/')
        self.assertContains(response, 'form-signin-heading')

    def test_post_login_wrong_input(self):
        found = resolve('/login', urlconf=adminpage.urls)
        request = Mock(wraps=HttpRequest(), method='POST')
        request.body = Mock()
        request.body.decode = Mock(return_value='{"username": "test", "password": "12345678"}')
        response = json.loads(found.func(request).content.decode())
        self.assertEqual(response['code'], 3)

# Create your tests here.
