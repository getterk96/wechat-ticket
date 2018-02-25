# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import Activity, Ticket

from datetime import *

# from wechat.tasks import GetTicket

import pytz, uuid

from django.db import transaction
from django.utils.timezone import localtime
from django.contrib import auth

__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):
    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):
    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):
    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):
    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):
    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):
    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


class GetActivityHandler(WeChatHandler):
    def check(self):
        return self.is_text('抢啥') or self.is_event_click(self.view.event_keys['check_activities'])

    def handle(self):
        activities = self.get_activities()
        if not activities.exists():
            return self.reply_text(self.get_message('book_empty'))
        set = []
        for activity in activities:
            if activity.end_time < datetime.utcnow().replace(tzinfo=pytz.timezone('UTC')):
                continue
            set.append({
                'Title': self.get_message("activity_title", title=activity.name),
                'PicUrl': activity.pic_url,
                'Url': self.url_activity({'id': activity.id}),
            })
        if not set:
            return self.reply_text(self.get_message('book_empty'))
        return self.reply_news(set)


class GetTicketHandler(WeChatHandler):
    def check(self):
        return self.is_get_ticket_text("抢票") or self.is_get_ticket_click()

    def handle(self):
        if not self.user.student_id:
            return self.reply_text("请先绑定学号= =！")

        with transaction.atomic():
            activity = self.get_activity_atomic()
            if activity:
                if activity.count() == 1:
                    activity = activity[0]
                    if activity.book_start < datetime.utcnow().replace(tzinfo=pytz.timezone('UTC')):
                        if activity.book_end > datetime.utcnow().replace(tzinfo=pytz.timezone('UTC')):
                            my_ticket = Ticket.objects.filter(activity=activity, student_id=self.user.student_id)
                            if not my_ticket.exists():
                                if activity.remain_tickets != 0:
                                    my_ticket = Ticket(unique_id=str(uuid.uuid4()), student_id=self.user.student_id,
                                                       activity=activity, status=1)
                                    my_ticket.save()
                                    activity.remain_tickets -= 1
                                    activity.save()
                                else:
                                    return self.reply_text("您没能抢到票，回去再练二十年手速吧！")
                            else:
                                my_ticket = my_ticket[0]
                            return self.reply_single_news({
                                'Title': self.get_message("ticket_title", act_name=my_ticket.activity.name,
                                                          status=my_ticket.status),
                                'PicUrl': my_ticket.activity.pic_url,
                                'Url': self.url_ticket({"openid": self.user.open_id, "ticket": my_ticket.unique_id})
                            })
                        else:
                            return self.reply_text("活动订票已结束")
                    else:
                        return self.reply_text("活动订票尚未开始")
                else:
                    return self.reply_text("存在重名活动，请利用菜单抢票")
            else:
                return self.reply_text("您要找的活动并不存在哦")


class ReturnTicketHandler(WeChatHandler):
    def check(self):
        return self.is_get_ticket_text("退票") or self.is_get_ticket_click()

    def handle(self):
        if not self.user.student_id:
            return self.reply_text("请先绑定学号= =！")
        with transaction.atomic():
            activities = self.get_activity_atomic()
            if activities:
                for activity in activities:
                    my_ticket = Ticket.objects.filter(activity=activity, student_id=self.user.student_id)
                    if not my_ticket.exists():
                        continue
                    else:
                        my_ticket = my_ticket[0]
                        if my_ticket.status == 1:
                            my_ticket.delete()
                            activity.remain_tickets += 1
                            activity.save()
                return self.reply_text("已退票")
            else:
                return self.reply_text("您要找的活动并不存在哦！")


class CheckTicketHandler(WeChatHandler):
    def check(self):
        return self.is_text('查票') or self.is_event_click(self.view.event_keys['check_ticket'])

    def handle(self):
        if not self.user.student_id:
            return self.reply_text("请先绑定学号= =！")
        my_tickets = Ticket.objects.filter(student_id=self.user.student_id)
        if not my_tickets.exists():
            return self.reply_text("您还没有任何电子票！")
        else:
            set = []
            for ticket in my_tickets:
                if ticket.status != 0 and ticket.activity.end_time < datetime.utcnow().replace(
                        tzinfo=pytz.timezone('UTC')):
                    ticket.status = 0
                    ticket.save()
                set.append({
                    'Title': self.get_message("ticket_title", act_name=ticket.activity.name, status=ticket.status),
                    'PicUrl': ticket.activity.pic_url,
                    'Url': self.url_ticket({"openid": self.user.open_id, "ticket": ticket.unique_id})
                })
            return self.reply_news(set)


class QuickResponseHandler(WeChatHandler):
    index = 0
    p = 0
    top = -1
    stack = []
    numsAndOps = ['(']
    sum = 0
    opsDict = {'+': 1, '-': 1, '*': 2, '/': 2, '(': 0, ')': 0}

    def pop(self):

        if self.top > -1:
            self.top -= 1

    def push(self, item):

        self.top += 1
        if self.top > len(self.stack) - 1:
            self.stack.append(item)
        else:
            self.stack[self.top] = item

    def check(self):

        for item in self.input['Content']:
            if not (item in "1234567890+-*/()"):
                return False

        self.index = 0
        self.p = 0
        self.top = -1
        self.stack = []
        self.numsAndOps = ['(']
        self.sum = 0

        try:
            for c in self.input['Content']:
                if c in "+-*/()":
                    if self.p != self.index:
                        self.numsAndOps.append(int(self.input['Content'][self.p:self.index]))
                    else:
                        if c != '(' and self.numsAndOps[self.top] != ')':
                            self.numsAndOps.append(0)
                    self.numsAndOps.append(c)
                    self.p = self.index + 1

                self.index += 1
            if self.p != self.index:
                self.numsAndOps.append(int(self.input['Content'][self.p:]))
            self.numsAndOps.append(')')
            for item in self.numsAndOps:
                if type(item) == int or type(item) == float:
                    self.push(item)
                else:
                    while True:
                        if item == '(':
                            self.push(item)
                            break
                        elif self.top > 0 and self.stack[self.top - 1] in "+-*/" and self.opsDict[item] <= self.opsDict[
                            self.stack[self.top - 1]]:
                            if self.stack[self.top - 1] == '+':
                                self.sum = self.stack[self.top - 2] + self.stack[self.top]
                            elif self.stack[self.top - 1] == '-':
                                self.sum = self.stack[self.top - 2] - self.stack[self.top]
                            elif self.stack[self.top - 1] == '*':
                                self.sum = self.stack[self.top - 2] * self.stack[self.top]
                            elif self.stack[self.top - 1] == '/':
                                self.sum = self.stack[self.top - 2] / self.stack[self.top]
                            self.pop()
                            self.pop()
                            self.pop()
                            self.push(self.sum)
                        else:
                            if item == ')':
                                self.sum = self.stack[self.top]
                                self.pop()
                                self.pop()
                                self.push(self.sum)
                            else:
                                self.push(item)
                            break

            self.sum = self.stack[0]

        except:

            return True

        return True

    def handle(self):
        if self.top == 0:
            return self.reply_text(str(self.sum))
        else:
            return self.reply_text("请输入正确的表达式！！")
