from django.conf.urls import url, include
from .views import *
#
app_name = 'api'

urlpatterns = [
    url(r'ping', ping, name="ping"),
    url(r'login$', login),
    url(r'create_user$', create_user),
    url(r'send_mail$', send_mail),
    url(r'(?P<folder_name>[\w\-]+)/get_mails$', get_mails),
    url(r'mail_id/(?P<mail_id>[0-9]+)/folder_name/(?P<folder_name>[\w\-]+)/mail_details$', get_mail_details),
    url(r'mail_events$', mail_events),
    url(r'mail_folder_data$', get_mail_folder_data),
    url(r'logout$', user_logout),
]