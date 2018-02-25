from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.test import TestCase

import WeChatTicket.urls
from wechat.wrapper import WeChatView

from unittest.mock import *
import xml.etree.ElementTree as ET


class GetTicketAndReturnTest(TestCase):
    fixtures = ["wechat_user.json", "wechat_activity.json", "wechat_ticket.json"]

    def test_get_ticket_success(self):
        found = resolve('/wechat', urlconf=WeChatTicket.urls)
        request = Mock(wraps=HttpRequest(), method='POST')
        request.body = '<xml>' \
                       '<ToUserName><![CDATA[1]]></ToUserName>\n' \
                       '<FromUserName><![CDATA[1]]></FromUserName>\n' \
                       '<MsgType><![CDATA[event]]></MsgType>\n' \
                       '<Event><![CDATA[CLICK]]></Event>\n' \
                       '<EventKey><![CDATA[BOOKING_ACTIVITY_1]]></EventKey>\n' \
                       '</xml>'
        content = found.func(request).content.decode(encoding="utf-8")
        response = WeChatView.parse_msg_xml(ET.fromstring(content))
        self.assertEqual(response['MsgType'], 'news')

    def test_get_ticket_failed_for_booking_late(self):
        found = resolve('/wechat', urlconf=WeChatTicket.urls)
        request = Mock(wraps=HttpRequest(), method='POST')
        request.body = '<xml>' \
                       '<ToUserName><![CDATA[1]]></ToUserName>\n' \
                       '<FromUserName><![CDATA[1]]></FromUserName>\n' \
                       '<MsgType><![CDATA[event]]></MsgType>\n' \
                       '<Event><![CDATA[CLICK]]></Event>\n' \
                       '<EventKey><![CDATA[BOOKING_ACTIVITY_2]]></EventKey>\n' \
                       '</xml>'
        content = found.func(request).content.decode(encoding="utf-8")
        response = WeChatView.parse_msg_xml(ET.fromstring(content))
        self.assertEqual(response['Content'], '活动订票已结束')

    def test_get_ticket_failed_for_booking_early(self):
        found = resolve('/wechat', urlconf=WeChatTicket.urls)
        request = Mock(wraps=HttpRequest(), method='POST')
        request.body = '<xml>' \
                       '<ToUserName><![CDATA[1]]></ToUserName>\n' \
                       '<FromUserName><![CDATA[1]]></FromUserName>\n' \
                       '<MsgType><![CDATA[event]]></MsgType>\n' \
                       '<Event><![CDATA[CLICK]]></Event>\n' \
                       '<EventKey><![CDATA[BOOKING_ACTIVITY_3]]></EventKey>\n' \
                       '</xml>'
        content = found.func(request).content.decode(encoding="utf-8")
        response = WeChatView.parse_msg_xml(ET.fromstring(content))
        self.assertEqual(response['Content'], '活动订票尚未开始')

    def test_get_ticket_failed_for_out_of_tickets(self):
        found = resolve('/wechat', urlconf=WeChatTicket.urls)
        request = Mock(wraps=HttpRequest(), method='POST')
        request.body = '<xml>' \
                       '<ToUserName><![CDATA[1]]></ToUserName>\n' \
                       '<FromUserName><![CDATA[1]]></FromUserName>\n' \
                       '<MsgType><![CDATA[event]]></MsgType>\n' \
                       '<Event><![CDATA[CLICK]]></Event>\n' \
                       '<EventKey><![CDATA[BOOKING_ACTIVITY_4]]></EventKey>\n' \
                       '</xml>'
        content = found.func(request).content.decode(encoding="utf-8")
        response = WeChatView.parse_msg_xml(ET.fromstring(content))
        self.assertEqual(response['Content'], '您没能抢到票，回去再练二十年手速吧！')

    def test_get_ticket_failed_for_already_have_ticket(self):
        found = resolve('/wechat', urlconf=WeChatTicket.urls)
        request = Mock(wraps=HttpRequest(), method='POST')
        request.body = '<xml>' \
                       '<ToUserName><![CDATA[1]]></ToUserName>\n' \
                       '<FromUserName><![CDATA[1]]></FromUserName>\n' \
                       '<MsgType><![CDATA[event]]></MsgType>\n' \
                       '<Event><![CDATA[CLICK]]></Event>\n' \
                       '<EventKey><![CDATA[BOOKING_ACTIVITY_5]]></EventKey>\n' \
                       '</xml>'
        content = found.func(request).content.decode(encoding="utf-8")
        response = ET.fromstring(content)
        url = response[5][0][3].text
        result = str.find(url, "3739b75a-03e6-4911-96c0-5a28e821943d") > 0
        self.assertEqual(result, True)

    def test_get_ticket_failed_for_same_name_activities(self):
        found = resolve('/wechat', urlconf=WeChatTicket.urls)
        request = Mock(wraps=HttpRequest(), method='POST')
        request.body = '<xml>' \
                       '<ToUserName><![CDATA[1]]></ToUserName>\n' \
                       '<FromUserName><![CDATA[1]]></FromUserName>\n' \
                       '<MsgType><![CDATA[text]]></MsgType>\n' \
                       '<Content><![CDATA[抢票 马兰花开]]></Content>\n' \
                       '</xml>'
        content = found.func(request).content.decode(encoding="utf-8")
        response = WeChatView.parse_msg_xml(ET.fromstring(content))
        self.assertEqual(response['Content'], '存在重名活动，请利用菜单抢票')

    def test_get_ticket_failed_for_no_such_activity(self):
        found = resolve('/wechat', urlconf=WeChatTicket.urls)
        request = Mock(wraps=HttpRequest(), method='POST')
        request.body = '<xml>' \
                       '<ToUserName><![CDATA[1]]></ToUserName>\n' \
                       '<FromUserName><![CDATA[1]]></FromUserName>\n' \
                       '<MsgType><![CDATA[text]]></MsgType>\n' \
                       '<Content><![CDATA[抢票 aaa]]></Content>\n' \
                       '</xml>'
        content = found.func(request).content.decode(encoding="utf-8")
        response = WeChatView.parse_msg_xml(ET.fromstring(content))
        self.assertEqual(response['Content'], '您要找的活动并不存在哦')

    def test_return_ticket_success(self):
        found = resolve('/wechat', urlconf=WeChatTicket.urls)
        request = Mock(wraps=HttpRequest(), method='POST')
        request.body = '<xml>' \
                       '<ToUserName><![CDATA[1]]></ToUserName>\n' \
                       '<FromUserName><![CDATA[1]]></FromUserName>\n' \
                       '<MsgType><![CDATA[text]]></MsgType>\n' \
                       '<Content><![CDATA[退票 马兰花开]]></Content>\n' \
                       '</xml>'
        content = found.func(request).content.decode(encoding="utf-8")
        response = WeChatView.parse_msg_xml(ET.fromstring(content))
        self.assertEqual(response['Content'], '已退票')

    def test_return_ticket_failed_for_acitvity_not_exist(self):
        found = resolve('/wechat', urlconf=WeChatTicket.urls)
        request = Mock(wraps=HttpRequest(), method='POST')
        request.body = '<xml>' \
                       '<ToUserName><![CDATA[1]]></ToUserName>\n' \
                       '<FromUserName><![CDATA[1]]></FromUserName>\n' \
                       '<MsgType><![CDATA[text]]></MsgType>\n' \
                       '<Content><![CDATA[退票 aaa]]></Content>\n' \
                       '</xml>'
        content = found.func(request).content.decode(encoding="utf-8")
        response = WeChatView.parse_msg_xml(ET.fromstring(content))
        self.assertEqual(response['Content'], '您要找的活动并不存在哦！')

    def test_get_or_return_ticket_failed_for_not_binded(self):
        found = resolve('/wechat', urlconf=WeChatTicket.urls)
        request = Mock(wraps=HttpRequest(), method='POST')
        request.body = '<xml>' \
                       '<ToUserName><![CDATA[2]]></ToUserName>\n' \
                       '<FromUserName><![CDATA[2]]></FromUserName>\n' \
                       '<MsgType><![CDATA[event]]></MsgType>\n' \
                       '<Event><![CDATA[CLICK]]></Event>\n' \
                       '<EventKey><![CDATA[BOOKING_ACTIVITY_1]]></EventKey>\n' \
                       '</xml>'
        content = found.func(request).content.decode(encoding="utf-8")
        response = WeChatView.parse_msg_xml(ET.fromstring(content))
        self.assertEqual(response['Content'], '请先绑定学号= =！')

# Create your tests here.
