from codex.baseerror import *
from codex.baseview import APIView

import time, requests

from wechat.models import User, Activity, Ticket


class UserBind(APIView):
    def validate_user(self):
        feed_back = requests.post("https://sslvpn.tsinghua.edu.cn/dana-na/auth/url_default/login.cgi",
                                  data={
                                      'tz_offset': 480,
                                      'password': self.input['password'],
                                      'realm': 'ldap',
                                      'username': self.input['student_id'],
                                  },
                                  verify=False)
        if "failed" in feed_back.url:
            raise ValidateError('学号或密码输入错误')

    def get(self):
        self.check_input('openid')
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()


class UserActivity(APIView):
    def get(self):
        self.check_input('id')
        try:
            activity = Activity.objects.get(id=self.input['id'])
        except:
            raise LogicError("活动并不存在")

        if activity.status != 1:
            raise LogicError("活动尚未发布")
        return {
            'name': activity.name,
            'key': activity.key,
            'description': activity.description,
            'startTime': time.mktime(activity.start_time.timetuple()),
            'endTime': time.mktime(activity.end_time.timetuple()),
            'place': activity.place,
            'bookStart': time.mktime(activity.book_start.timetuple()),
            'bookEnd': time.mktime(activity.book_end.timetuple()),
            'totalTickets': activity.total_tickets,
            'picUrl': activity.pic_url,
            'remainTickets': activity.remain_tickets,
            'currentTime': int(time.time()),
        }


class UserTicket(APIView):
    def get(self):
        self.check_input('openid', 'ticket')
        try:
            ticket = Ticket.objects.get(unique_id=self.input['ticket'])
        except:
            raise ValidateError("您已退票")

        user = User.objects.filter(student_id=ticket.student_id)[0]
        if user.open_id == self.input['openid']:
            activity = ticket.activity
            return {
                'activityName': activity.name,
                'place': activity.place,
                'activityKey': activity.key,
                'uniqueId': ticket.unique_id,
                'startTime': time.mktime(activity.start_time.timetuple()),
                'endTime': time.mktime(activity.end_time.timetuple()),
                'currentTime': int(time.time()),
                'status': ticket.status,
            }

        else:
            raise ValidateError("归属权已过期")
