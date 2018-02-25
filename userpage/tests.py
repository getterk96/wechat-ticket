from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.test import TestCase

from userpage.views import UserBind
import userpage.urls, json

from unittest.mock import *


class BindTest(TestCase):
    fixtures = ['userpage_user.json']

    def test_u_bind(self):
        response = self.client.get('/u/bind/')
        self.assertContains(response, 'inputUsername')

    def test_get_already_binded(self):
        found = resolve('/user/bind', urlconf=userpage.urls)
        request = Mock(wraps=HttpRequest(), method='GET')
        request.body = Mock()
        request.body.decode = Mock(return_value='{"openid": "1"}')
        response = json.loads(found.func(request).content.decode())
        self.assertEqual(response['data'], "1")

    def test_get_not_binded(self):
        found = resolve('/user/bind', urlconf=userpage.urls)
        request = Mock(wraps=HttpRequest(), method='GET')
        request.body = Mock()
        request.body.decode = Mock(return_value='{"openid": "2"}')
        response = json.loads(found.func(request).content.decode())
        self.assertEqual(response['data'], "")

    def test_post_bad_username_password(self):
        found = resolve('/user/bind', urlconf=userpage.urls)
        request = Mock(wraps=HttpRequest(), method='POST')
        request.body = Mock()
        request.body.decode = Mock(return_value='{"openid": "2", "student_id": "3", "password": "1"}')
        response = json.loads(found.func(request).content.decode())
        self.assertEqual(response['code'], 3)

    def test_post_good_username_password(self):
        found = resolve('/user/bind', urlconf=userpage.urls)
        request = Mock(wraps=HttpRequest(), method='POST')
        request.body = Mock()
        request.body.decode = Mock(return_value='{"openid": "2", "student_id": "4", "password": "1"}')
        with patch.object(UserBind, 'validate_user', return_value=None) as MockValid:
            response = json.loads(found.func(request).content.decode())
            self.assertEqual(response['code'], 0)

class ActivityTest(TestCase):
    fixtures = ['userpage_activity.json', 'userpage_user.json', 'userpage_ticket.json']

    def test_u_activity(self):
        response = self.client.get('/u/activity/')
        self.assertContains(response, 'timer-wrapper')

    def test_get_activity_exists(self):
        found = resolve('/activity/detail', urlconf=userpage.urls)
        request = Mock(wraps=HttpRequest(), method='GET')
        request.body = Mock()
        request.body.decode = Mock(return_value='{"id": "1"}')
        response = json.loads(found.func(request).content.decode())
        self.assertEqual(response['data']['name'], '\u9a6c\u5170\u82b1\u5f00')

    def test_get_activity_not_published(self):
        found = resolve('/activity/detail', urlconf=userpage.urls)
        request = Mock(wraps=HttpRequest(), method='GET')
        request.body = Mock()
        request.body.decode = Mock(return_value='{"id": "2"}')
        response = json.loads(found.func(request).content.decode())
        self.assertEqual(response['msg'], '活动尚未发布')

    def test_get_activity_not_exist(self):
        found = resolve('/activity/detail', urlconf=userpage.urls)
        request = Mock(wraps=HttpRequest(), method='GET')
        request.body = Mock()
        request.body.decode = Mock(return_value='{"id": "3"}')
        response = json.loads(found.func(request).content.decode())
        self.assertEqual(response['msg'], '活动并不存在')

class TicketTest(TestCase):
    fixtures = ['userpage_activity.json', 'userpage_user.json', 'userpage_ticket.json']

    def test_u_activity(self):
        response = self.client.get('/u/ticket/')
        self.assertContains(response, 'ticket-wrapper')

    def test_get_ticket_get_successfully(self):
        found = resolve('/ticket/detail', urlconf=userpage.urls)
        request = Mock(wraps=HttpRequest(), method='GET')
        request.body = Mock()
        request.body.decode = Mock(return_value='{"openid": "1", "ticket": "3739b75a-03e6-4911-96c0-5a28e821943d"}')
        response = json.loads(found.func(request).content.decode())
        self.assertEqual(response['data']['activityName'], '\u9a6c\u5170\u82b1\u5f00')

    def test_get_ticket_get_failed_for_already_returned(self):
        found = resolve('/ticket/detail', urlconf=userpage.urls)
        request = Mock(wraps=HttpRequest(), method='GET')
        request.body = Mock()
        request.body.decode = Mock(return_value='{"openid": "1", "ticket": "3739b75a-03e6-4911-96c0-5a28e821943h"}')
        response = json.loads(found.func(request).content.decode())
        self.assertEqual(response['msg'], '您已退票')

    def test_get_ticket_get_failed_for_not_the_correct_user(self):
        found = resolve('/ticket/detail', urlconf=userpage.urls)
        request = Mock(wraps=HttpRequest(), method='GET')
        request.body = Mock()
        request.body.decode = Mock(return_value='{"openid": "1", "ticket": "3739b75a-03e6-4911-96c0-5a28e821943g"}')
        response = json.loads(found.func(request).content.decode())
        self.assertEqual(response['msg'], '归属权已过期')

# Create your tests here.
