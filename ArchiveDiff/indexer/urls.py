from django.conf.urls.defaults import *
from celery.task.builtins import PingTask
from celery import views as celery_views
from indexer.tasks import *

urlpatterns = patterns('',
    (r'^$', 'indexer.views.list'),
    url(r'^process/$', celery_views.apply,{'task_name':'warc.index'}),
    url(r'^ping/', celery_views.task_view(PingTask)),
    url(r'^(?P<task_id>[\w\d\-]+)/done/?$', celery_views.is_task_successful,name="celery-is_task_successful"),
    url(r'^(?P<task_id>[\w\d\-]+)/status/?$', celery_views.task_status,name="celery-task_status"),
)


