from django.conf.urls import patterns, url
import views
from . import APP_NAME


urlpatterns = patterns('',
   url(r'^$', views.map_list, name='%s.list' % APP_NAME),
   url(r'^(?P<map_id>\d+)/view/$', views.view_map, name='%s.view' % APP_NAME),
   url(r'^(?P<map_id>\d+)/embed/$', views.embed_map, name='%s.embed' % APP_NAME),
   url(r'^(?P<map_id>\d+)/edit/$', views.edit_map, name='%s.edit' % APP_NAME),
   url(r'^new/$', views.new_map, name='%s.new' % APP_NAME),
   url(r'^map_layers/(?P<map_id>\d+)/$', views.map_layers, name='%s.map_layers' % APP_NAME),
)