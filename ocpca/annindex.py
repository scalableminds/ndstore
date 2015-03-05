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

import numpy as np
import array
import cStringIO
import tempfile
import h5py

import ocpcaproj

import logging
logger=logging.getLogger("ocp")

#
# AnnotateIndex: Maintain the index in the database
# AUTHOR: Priya Manavalan
#

class AnnotateIndex:

  def __init__(self,kvio,proj):
    """Give an active connection.This puts all index operations in the same transation as the calling db."""

    self.proj = proj
    self.kvio = kvio

    if self.proj.getKVEngine() == 'MySQL':
      self.NPZ = True
    else: 
      self.NPZ = False
   

  def getIndex ( self, entityid, resolution, update=False ):
    """Retrieve the index for the annotation with id"""  
    
    idxstr = self.kvio.getIndex ( entityid, resolution, update )
    if idxstr:
      if self.NPZ:
        fobj = cStringIO.StringIO ( idxstr )
        return np.load ( fobj )      
      else:
        # cubes are HDF5 files
        with closing (tempfile.NamedTemporaryFile ()) as tmpfile:
          tmpfile.write ( idxstr )
          tmpfile.seek(0)
          h5 = h5py.File ( tmpfile.name ) 
  
          # load the numpy array
          return np.array ( h5['index'] )
    else:
      return []
       
  
  def putIndex ( self, entityid, resolution, index, update=False ):
    """Write the index for the annotation with id"""

    if self.NPZ:
      fileobj = cStringIO.StringIO ()
      np.save ( fileobj, index )
      self.kvio.putIndex ( entityid, resolution, fileobj.getvalue(), update )
    else:

      with closing ( tempfile.NamedTemporaryFile () ) as tmpfile:
        h5 = h5py.File ( tmpfile.name )
        h5.create_dataset ( "index", tuple(index.shape), index.dtype,compression='gzip',  data=index )
        h5.close()
        tmpfile.seek(0)
        self.kvio.putIndex ( entityid, resolution, tmpfile.read(), update )


  def updateIndexDense(self,index,resolution):
    """Updated the database index table with the input index hash table"""

    for key, value in index.iteritems():
      cubelist = list(value)
      cubeindex=np.array(cubelist, dtype=np.uint64)
          
      curindex = self.getIndex(key,resolution,True)
         
      if curindex==[]:
        self.putIndex ( key, resolution, cubeindex, False )
            
      else:
        # Update index to the union of the currentIndex and the updated index
        newIndex=np.union1d(curindex,cubeindex)
        self.putIndex ( key, resolution, newIndex, True )

  
  def deleteIndexResolution ( self, annid, res ):
    """delete the index for a given annid at the given resolution"""
    
    # delete Index table for each resolution
    self.kvio.deleteIndex(annid,res)
  
  
  def deleteIndex ( self, annid, resolutions ):
    """delete the index for a given annid"""
    
    #delete Index table for each resolution
    for res in resolutions:
      self.kvio.deleteIndex(annid,res)


  def updateIndex ( self, entityid, index, resolution ):
    """Updated the database index table with the input index hash table"""

    curindex = self.getIndex ( entityid, resolution, True )

    if curindex == []:
        
        if self.NPZ:
          fileobj = cStringIO.StringIO ()
          np.save ( fileobj, index )
          self.kvio.putIndex ( entityid, resolution, fileobj.getvalue() )
        else:

          with closing ( tempfile.NamedTemporaryFile () ) as tmpfile:
            h5 = h5py.File ( tmpfile.name )
            h5.create_dataset ( "index", tuple(index.shape), index.dtype, compression='gzip',  data=index )
            h5.close()
            tmpfile.seek(0)
            self.kvio.putIndex ( entityid, resolution, tmpfile.read() )

    else :
        
        # Update Index to the union of the currentIndex and the updated index
        newIndex = np.union1d ( curindex, index )

        # Update the index in the database
        if self.NPZ:
          fileobj = cStringIO.StringIO ()
          np.save ( fileobj, newIndex )
          self.kvio.putIndex ( entityid, resolution, fileobj.getvalue(), True )
        else:

          with closing ( tempfile.NamedTemporaryFile () ) as tmpfile:
            h5 = h5py.File ( tmpfile.name )
            h5.create_dataset ( "index", tuple(index.shape), index.dtype, compression='gzip',  data=index )
            h5.close()
            tmpfile.seek(0)
            self.kvio.putIndex ( entityid, resolution, tmpfile.read(), True )
