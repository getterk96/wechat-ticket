# -*- coding: utf-8 -*-
#
from django.conf.urls import url

from userpage.views import *


__author__ = "Epsirom"


urlpatterns = [
    url(r'^user/bind/?$', UserBind.as_view()),
    url(r'^activity/detail/?$', UserActivity.as_view()),
    url(r'^ticket/detail/?$', UserTicket.as_view()),
]
