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

import urllib2
import cStringIO
import sys
import os
import tempfile
import h5py
import random 
import csv
import numpy as np
import pytest
import json
from contextlib import closing

from pytesthelpers import makeAnno

import ocpcaproj

import kvengine_to_test
import site_to_test
import makeunitdb

SITE_HOST = site_to_test.site

# Module level setup/teardown
def setup_module(module):
  pass
def teardown_module(module):
  pass


class TestOther:
  """Other interfaces to OCPCA that don't fit into other categories"""

  # Per method setup/teardown
#  def setup_method(self,method):
#    pass
#  def teardown_method(self,method):
#    pass

  def setup_class(self):
    """Create the unittest database"""
    makeunitdb.createTestDB('pubunittest', public=True)

  def teardown_class (self):
    """Destroy the unittest database"""
    makeunitdb.deleteTestDB('pubunittest')

  def test_public_tokens (self):
    """Test the function that shows the public tokens"""

    url =  "http://%s/ca/public_tokens/" % ( SITE_HOST )
    req = urllib2.Request ( url )
    f = urllib2.urlopen ( url )

    # reead the json data
    tokens = json.loads ( f.read() )
    assert ( "pubunittest" in tokens )

  def test_info(self):

    url =  "http://%s/ca/%s/info/" % ( SITE_HOST, 'pubunittest' )
    req = urllib2.Request ( url )
    f = urllib2.urlopen ( url )
    
    # reead the json data
    projinfo = json.loads ( f.read() )
    assert ( projinfo['project']['projecttype'] == 'annotation' )
    assert ( projinfo['dataset']['offset']['0'][2] == 1 )

  def test_reserve ( self ):
    """reserve 1000 ids twice and make sure that the numbers work"""
  
    url =  "http://%s/ca/%s/reserve/%s/" % ( SITE_HOST, 'pubunittest', 1000 )
    req = urllib2.Request ( url )
    f = urllib2.urlopen ( url )
    (id1, size1) = json.loads(f.read())
    f = urllib2.urlopen ( url )
    (id2, size2) = json.loads(f.read())

    assert ( id2-id1==1000 )
    assert ( size1 == size2 == 1000 )


