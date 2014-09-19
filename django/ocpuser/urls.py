from django.conf.urls import *
from ocpuser.views import *
import django.contrib.auth

# Uncomment the next two lines to enable the admin:                        
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('ocpuser.views',
                       url(r'^profile/$', 'profile'),
                       url(r'^datasets/', 'get_datasets'),
                       url(r'^token/$', 'tokens'),
                       url(r'^createproject/$', 'createproject'),
                       url(r'^updateproject/$', 'updateproject'),
                       url(r'^createdataset/$', 'createdataset'),
                       url(r'^updatedataset/$', 'updatedataset'),
                       url(r'^restore/$', 'restore'),
                       url(r'^download/$', 'download'),
                       
   
)
