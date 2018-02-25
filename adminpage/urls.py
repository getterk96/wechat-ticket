# -*- coding: utf-8 -*-
#
from django.conf.urls import url

from adminpage.views import *


__author__ = "Getterk"


urlpatterns = [
    url(r'^login/?$', AdminLogin.as_view()),
    url(r'^logout/?$', AdminLogout.as_view()),
    url(r'^activity/list/?$', AdminList.as_view()),
    url(r'^image/upload/?$', AdminUpload.as_view()),
    url(r'^activity/delete/?$', AdminDelete.as_view()),
    url(r'^activity/create/?$', AdminCreate.as_view()),
    url(r'^activity/detail/?$', AdminDetail.as_view()),
    url(r'^activity/menu/?$', AdminMenu.as_view()),
    url(r'^activity/checkin/?$', AdminCheckin.as_view()),
]