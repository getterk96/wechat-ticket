import time

from django.contrib import auth
from django.core.files.storage import default_storage

from codex.baseerror import *
from codex.baseview import APIView

from wechat.views import CustomWeChatView
from wechat.models import Activity, Ticket
from WeChatTicket.settings import SITE_DOMAIN


class AdminLogin(APIView):

    def get(self):
        if not self.request.user.is_authenticated:
            raise ValidateError("请先登录")

    def post(self):
        self.check_input('username', 'password')
        username = self.input['username']
        password = self.input['password']
        user = auth.authenticate(self.request, username=username, password=password)
        if user:
            if user.is_active:
                auth.login(self.request, user)
            else:
                raise ValidateError("用户状态异常")
        else:
            raise ValidateError("用户名或密码输入错误")


class AdminLogout(APIView):

    def post(self):
        user = self.request.user
        if user is not None:
            if user.is_active:
                auth.logout(self.request)
            else:
                raise LogicError("出现了奇怪的问题，我们已经记录下来了")
        else:
            raise LogicError("出现了奇怪的问题，我们已经记录下来了")


class AdminCreate(APIView):

    def post(self):
        self.check_input('name', 'key', 'place', 'description', 'picUrl', 'startTime', 'endTime', 'bookStart', 'bookEnd'
                         , 'status', 'totalTickets')
        user = self.request.user
        if user.is_authenticated:
            activity = Activity(
                name=self.input['name'],
                key=self.input['key'],
                place=self.input['place'],
                description=self.input['description'],
                pic_url=self.input['picUrl'],
                start_time=self.input['startTime'],
                end_time=self.input['endTime'],
                book_start=self.input['bookStart'],
                book_end=self.input['bookEnd'],
                status=self.input['status'],
                total_tickets=self.input['totalTickets'],
                remain_tickets=self.input['totalTickets'],
            )
            activity.save()

        else:
            raise ValidateError("请先登录")


class AdminList(APIView):
    def get(self):
        data = []
        user = self.request.user
        if user.is_authenticated:
            for activity in Activity.objects.all():
                act_data = {
                    'id': activity.id,
                    'name': activity.name,
                    'description': activity.description,
                    'startTime': time.mktime(activity.start_time.timetuple()),
                    'endTime': time.mktime(activity.end_time.timetuple()),
                    'place': activity.place,
                    'bookStart': time.mktime(activity.book_start.timetuple()),
                    'bookEnd': time.mktime(activity.book_end.timetuple()),
                    'currentTime': int(time.time()),
                    'status': activity.status,
                }
                data.append(act_data)
            return data

        else:
            raise ValidateError("请先登录")


class AdminDelete(APIView):
    def post(self):
        self.check_input('id')
        user = self.request.user
        if user.is_authenticated:
            activity = Activity.objects.get(id=self.input['id'])
            tickets = Ticket.objects.filter(activity=activity)
            if tickets.exists():
                for ti in tickets:
                    ti.delete()
            activity.delete()
        else:
            raise ValidateError("请先登录")


class AdminDetail(APIView):

    def get(self):
        self.check_input('id')
        user = self.request.user
        if user.is_authenticated:
            activity = Activity.objects.get(id = self.input['id'])
            data = {
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
                'bookedTickets': activity.total_tickets - activity.remain_tickets,
                'usedTickets': Ticket.objects.filter(activity=activity, status=2).count(),
                'currentTime': int(time.time()),
                'status': activity.status,
            }
            return data

        else:
            raise ValidateError("请先登录")

    def post(self):
        self.check_input('name', 'place', 'description', 'picUrl', 'startTime', 'endTime', 'bookStart', 'bookEnd'
                         , 'status', 'totalTickets')
        user = self.request.user
        if user.is_authenticated:
            activity = Activity.objects.get(id=self.input['id'])
            activity.name = self.input['name']
            activity.place = self.input['place']
            activity.description = self.input['description']
            activity.pic_url = self.input['picUrl']
            activity.start_time = self.input['startTime']
            activity.end_time = self.input['endTime']
            activity.book_start = self.input['bookStart']
            activity.book_end = self.input['bookEnd']
            activity.status=self.input['status']
            activity.total_tickets = self.input['totalTickets']
            activity.save()

        else:
            raise ValidateError("请先登录")


class AdminMenu(APIView):
    def get(self):
        user = self.request.user
        if user.is_authenticated:
            menu = CustomWeChatView.lib.get_wechat_menu()
            sub_buttons = menu[-1]['sub_button']
            sub_names = []
            for sub in sub_buttons:
                sub_names.append(sub['name'])
            data = []
            for activity in Activity.objects.all():
                act_data = {
                    'id': activity.id,
                    'name': activity.name,
                    'menuIndex': sub_names.index(activity.name) + 1 if activity.name in sub_names else 0,
                }
                data.append(act_data)
            return data

        else:
            raise ValidateError("请先登录")

    def post(self):
        user = self.request.user
        if user.is_authenticated:
            activities = []
            for id in self.input:
                activity = Activity.objects.get(id = id)
                activities.append(activity)
            CustomWeChatView.update_menu(activities)

        else:
            raise ValidateError("请先登录")


class AdminCheckin(APIView):
    def post(self):
        self.check_input('actId')
        user = self.request.user
        if user.is_authenticated:
            self.check_input('actId')
            activity = Activity.objects.get(id=self.input['actId'])
            try:
                if 'ticket' in self.input.keys():
                    ticket = Ticket.objects.get(unique_id=self.input['ticket'], activity=activity)
                else:
                    ticket = Ticket.objects.get(student_id=self.input['studentId'], activity=activity)
            except:
                raise ValidateError("信息有误，请重试")
            ticket.status = 2
            ticket.save()
            return {'ticket':ticket.unique_id, 'studentId':ticket.student_id}

        else:
            raise ValidateError("请先登录")


class AdminUpload(APIView):
    def post(self):
        self.check_input('image')
        user = self.request.user
        if user.is_authenticated:
            data = self.input['image'][0]
            path = default_storage.save('img/' + data.name, data)
            return SITE_DOMAIN + '/media/' + path

        else:
            raise ValidateError("请先登录")