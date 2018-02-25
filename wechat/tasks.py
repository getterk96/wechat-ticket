from wechat.models import Ticket

from celery import task
from datetime import *

import pytz

@task
def GetTicket(handler):
    activity = handler.get_activity()
    if activity:
        if activity.book_start < datetime.utcnow().replace(tzinfo=pytz.timezone('UTC')):
            if activity.book_end > datetime.utcnow().replace(tzinfo=pytz.timezone('UTC')):
                act_tickets = Ticket.objects.filter(activity=activity)
                my_ticket = act_tickets.filter(student_id=handler.user.student_id)
                if not my_ticket.exists():
                    if activity.remain_tickets != 0:
                        ticket = act_tickets.filter(student_id="")[0]
                        if ticket:
                            ticket.student_id = handler.user.student_id
                            ticket.save()
                            activity.remain_tickets -= 1
                            activity.save()
                            my_ticket = ticket
                    else:
                        return handler.reply_text("您没能抢到票，回去再练二十年手速吧！")
                else:
                    my_ticket = my_ticket[0]
                return handler.reply_single_news({
                    'Title': handler.get_message("ticket_title", act_name=my_ticket.activity.name),
                    'PicUrl': my_ticket.activity.pic_url,
                    'Url': handler.url_ticket({"openid": handler.user.open_id, "ticket": my_ticket.unique_id})
                })
            else:
                return handler.reply_text("活动订票已结束！")
        else:
            return handler.reply_text("活动订票尚未开始！")
    else:
        return handler.reply_text("您要找的活动并不存在哦！")
