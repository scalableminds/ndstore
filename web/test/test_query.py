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

from pytesthelpers import makeAnno

EM_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".." ))
EM_EMCA_PATH = os.path.join(EM_BASE_PATH, "emca" )
sys.path += [ EM_EMCA_PATH ]

#SITE_HOST = 'openconnecto.me'
SITE_HOST = 'localhost:8000'
#SITE_HOST = 'localhost'

import emcaproj

# Module level setup/teardown
def setup_module(module):
  pass
def teardown_module(module):
  pass


class TestRamon:

  # Per method setup/teardown
#  def setup_method(self,method):
#    pass
#  def teardown_method(self,method):
#    pass

  def setup_class(self):
    """Create the unittest database"""

    self.pd = emcaproj.EMCAProjectsDB()
    self.pd.newEMCAProj ( 'unittest', 'test', 'localhost', 'unittest', 2, 'kasthuri11', None, False, True )

  def teardown_class (self):
    """Destroy the unittest database"""
    print "in teardown_class"
    self.pd.deleteEMCADB ('unittest')



  def test_query (self):
    """Test the function that lists objects of different types."""

    # synapse annotations
    anntype = 2
    status = random.randint(0,100)
    confidence = random.random()*0.3+0.1   # number between 0.1 and 0.4
    synapse_type = random.randint(0,100)
    synapse_weight = random.random()*0.9+0.1   # number between 0.1 and 0.9

    for i in range (10):

      # Make an annotation 
      annid = makeAnno ( anntype, SITE_HOST )

      # set some fields in the even annotations
      if i % 2 == 0:
        url =  "http://%s/emca/%s/%s/setField/status/%s/" % ( SITE_HOST, 'unittest',str(annid), status )
        req = urllib2.Request ( url )
        f = urllib2.urlopen ( url )
        assert f.read()==''

        # set the confidence
        url =  "http://%s/emca/%s/%s/setField/confidence/%s/" % ( SITE_HOST, 'unittest',str(annid), confidence )
        req = urllib2.Request ( url )
        f = urllib2.urlopen ( url )
        assert f.read()==''

        # set the type
        url =  "http://%s/emca/%s/%s/setField/synapse_type/%s/" % ( SITE_HOST, 'unittest',str(annid), synapse_type )
        req = urllib2.Request ( url )
        f = urllib2.urlopen ( url )
        assert f.read()==''

      # set some fields in the even annotations
      if i % 2 == 1:
        # set the confidence
        url =  "http://%s/emca/%s/%s/setField/confidence/%s/" % ( SITE_HOST, 'unittest',str(annid), 1.0-confidence )
        req = urllib2.Request ( url )
        f = urllib2.urlopen ( url )
        assert f.read()==''

            
    # check the status 
    url =  "http://%s/emca/%s/query/status/%s/" % ( SITE_HOST, 'unittest', status )
    req = urllib2.Request ( url )
    f = urllib2.urlopen ( url )
    retfile = tempfile.NamedTemporaryFile ( )
    retfile.write ( f.read() )
    retfile.tell()
    h5ret = h5py.File ( retfile.name, driver='core', backing_store=False )
    assert h5ret['ANNOIDS'].shape[0] ==5

    # check all the confidence variants 
    url =  "http://%s/emca/%s/query/confidence/%s/%s/" % ( SITE_HOST, 'unittest', 'lt', 1.0-confidence-0.0001 )
    req = urllib2.Request ( url )
    f = urllib2.urlopen ( url )
    retfile = tempfile.NamedTemporaryFile ( )
    retfile.write ( f.read() )
    retfile.tell()
    h5ret = h5py.File ( retfile.name, driver='core', backing_store=False )
    assert h5ret['ANNOIDS'].shape[0] ==5

    url =  "http://%s/emca/%s/query/confidence/%s/%s/" % ( SITE_HOST, 'unittest', 'gt', confidence+0.00001 )
    req = urllib2.Request ( url )
    f = urllib2.urlopen ( url )
    retfile = tempfile.NamedTemporaryFile ( )
    retfile.write ( f.read() )
    retfile.tell()
    h5ret = h5py.File ( retfile.name, driver='core', backing_store=False )
    assert h5ret['ANNOIDS'].shape[0] ==5

    # check the synapse_type 
    url =  "http://%s/emca/%s/query/synapse_type/%s/" % ( SITE_HOST, 'unittest', synapse_type )
    req = urllib2.Request ( url )
    f = urllib2.urlopen ( url )
    retfile = tempfile.NamedTemporaryFile ( )
    retfile.write ( f.read() )
    retfile.tell()
    h5ret = h5py.File ( retfile.name, driver='core', backing_store=False )
    assert h5ret['ANNOIDS'].shape[0] ==5

    # check the synapse_weight 
    url =  "http://%s/emca/%s/query/synapse_weight/%s/%s/" % ( SITE_HOST, 'unittest', 'gt', confidence-0.00001 )
    req = urllib2.Request ( url )
    f = urllib2.urlopen ( url )
    retfile = tempfile.NamedTemporaryFile ( )
    retfile.write ( f.read() )
    retfile.tell()
    h5ret = h5py.File ( retfile.name, driver='core', backing_store=False )
    assert h5ret['ANNOIDS'].shape[0] ==5
