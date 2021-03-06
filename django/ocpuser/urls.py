# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls import *
from ocpuser.views import *
import django.contrib.auth

# Uncomment the next two lines to enable the admin:                        
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('ocpuser.views',
                       url(r'^profile/$', 'getProjects'),
                       url(r'^projects/$', 'getProjects'),
                       url(r'^datasets/$', 'getDatasets'),
                       url(r'^channels/$', 'getChannels'),
                       url(r'^token/$', 'getTokens'),
                       url(r'^alltokens/$', 'getAllTokens'),
                       url(r'^createproject/$', 'createProject'),
                       url(r'^createdataset/$', 'createDataset'),
                       url(r'^createtoken/$', 'createToken'),
                       url(r'^updateproject/$', 'updateProject'),
                       url(r'^updatetoken/$', 'updateToken'),
                       url(r'^updatechannel/$', 'updateChannel'),
                       url(r'^updatedataset/$', 'updateDataset'),
                       url(r'^backupproject/$', 'backupProject'),
                       url(r'^restoreproject/$', 'restoreProject'),
                       url(r'^download/$', 'downloadData'),
)
