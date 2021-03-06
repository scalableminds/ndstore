#/p Copyright 2014 Open Connectome Project (http://openconnecto.me)
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


import numpy as np
import json
import urllib2
from lxml import etree
from django.conf import settings

import ocpcadb
from ocptype import ZSLICES

import logging
logger=logging.getLogger("ocp")


def projdict ( proj ):

  projdict = {}
  projdict['name'] = proj.getProjectName()
  projdict['description'] = proj.getProjectDescription()
  projdict['version'] = proj.getOCPVersion()

  # These fields are internal
  #projdict['dbname'] = proj._dbname
  #projdict['host'] = proj._dbhost
  #projdict['schemaversion'] = proj.getSchemaVersion()
  #projdict['kvengine'] = proj._kvengine
  #projdict['kvserver'] = proj._kvserver

  return projdict

def datasetdict ( dataset ):

  dsdict = {}
  dsdict['name'] = dataset.getDatasetName()
  dsdict['scalinglevels'] = dataset.scalinglevels
  if dataset.scalingoption == ZSLICES:
    dsdict['scaling'] = 'zslices'
  else:
    dsdict['scaling'] = 'xyz'
  dsdict['resolutions'] = dataset.resolutions
  dsdict['imagesize'] = dataset.imagesz
  dsdict['offset'] = dataset.offset
  dsdict['voxelres'] = dataset.voxelres
  dsdict['cube_dimension'] = dataset.cubedim
  # Stephan projinfo
  dsdict['neariso_scaledown'] = dataset.nearisoscaledown
  dsdict['neariso_offset'] = dataset.neariso_offset
  dsdict['neariso_voxelres'] = dataset.neariso_voxelres
  dsdict['neariso_imagesize'] = dataset.neariso_imagesz
  # Figure out neariso in new design
  dsdict['timerange'] = dataset.timerange
  dsdict['description'] = dataset.getDatasetDescription()

  return dsdict

def chandict ( channel ):
  chandict = {}
  chandict['channel_type'] = channel.getChannelType()
  chandict['datatype'] = channel.getDataType()
  chandict['exceptions'] = channel.getExceptions()
  chandict['readonly'] = channel.getReadOnly()
  chandict['resolution'] = channel.getResolution()
  chandict['propagate'] = channel.getPropagate()
  chandict['windowrange'] = channel.getWindowRange()
  chandict['description'] = channel.getChannelDescription()

  return chandict

def jsonInfo (proj):
  """All Project Info"""

  jsonprojinfo = {}
  jsonprojinfo['dataset'] = datasetdict ( proj.datasetcfg )
  jsonprojinfo['project'] = projdict ( proj )
  jsonprojinfo['channels'] = {}
  for ch in proj.projectChannels():
    jsonprojinfo['channels'][ch.getChannelName()] = chandict ( ch ) 
  
  jsonprojinfo['metadata'] = metadatadict( proj )
  return json.dumps ( jsonprojinfo, sort_keys=True, indent=4 )

def xmlInfo (token, proj):
  """All Project Info"""
  
  jsonprojinfo = {}
  jsonprojinfo['dataset'] = datasetdict ( proj.datasetcfg )
  jsonprojinfo['project'] = projdict ( proj )
  jsonprojinfo['channels'] = {}
  for ch in proj.projectChannels():
    jsonprojinfo['channels'][ch.getChannelName()] = chandict ( ch ) 
  jsonprojinfo['metadata'] = metadatadict( proj )
  
  root = etree.Element('Volume', InputChecksum="", host="http://openconnecto.me/ocptilecache/tilecache/viking/", name=token, num_sections=str(jsonprojinfo['dataset']['imagesize'][0][2]), num_stos="0", path="http://openconnecto.me/ocptilecache/tilecache/viking/")
  etree.SubElement(root, 'Scale', UnitsOfMeasure="nm", UnitsPerPixel=str(jsonprojinfo['dataset']['voxelres'][0][0]/jsonprojinfo['dataset']['voxelres'][0][1]))
  tileserver_element = etree.SubElement(root, 'OCPTileServer', CoordSpaceName="volume", host="http://openconnecto.me/ocptilecache/tilecache/viking/", FilePrefix="", FilePostfix=".png", TileXDim="512", TileYDim="512", GridXdim=str(jsonprojinfo['dataset']['imagesize'][0][0]/512), GridYDim=str(jsonprojinfo['dataset']['imagesize'][0][1]/512), MaxLevel=str(jsonprojinfo['dataset']["resolutions"][-1]))
  for channel_name in jsonprojinfo['channels'].keys():
    etree.SubElement(tileserver_element, "Channel", Name=channel_name, Path=channel_name, Datatype=jsonprojinfo['channels'][channel_name]['datatype'])
  for slice_number in range(jsonprojinfo['dataset']['offset'][0][2], jsonprojinfo['dataset']['offset'][0][2]+jsonprojinfo['dataset']['imagesize'][0][2]):
    etree.SubElement(root, "Section", Number="{}".format(slice_number))
  
  return etree.tostring(root)

def metadatadict( proj ):
  """Metadata Info"""
  if settings.LIMS_SERVER_ENABLED:
    try:
      url = 'http://{}/metadata/ocp/get/{}/'.format(settings.LIMS_SERVER, proj.getProjectName())
      req = urllib2.Request(url)
      response = urllib2.urlopen(req, timeout=0.5)
      return json.loads(response.read())
    except urllib2.URLError, e:
      print "Failed URL {}".format(url)
      return {}
  else:
    return {}

def publicTokens ( projdb ):
  """List of Public Tokens"""
  
  tokens = projdb.getPublic ()
  return json.dumps (tokens, sort_keys=True, indent=4)
