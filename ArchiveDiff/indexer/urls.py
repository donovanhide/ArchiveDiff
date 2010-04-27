from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'indexer.views.list'),
    (r'^process$', 'indexer.views.process'),
)
