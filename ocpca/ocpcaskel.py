# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
#Licensed under the Apache License, Version 2.0 (the "License");
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

import re

import annotation

      
def ingestSWC ( swcfile, ch, db ):
  """Ingest the SWC file into a database.  This will involve:
        parsing out separate connected components as skeletons
        deduplicating nodes (for Vaa3d) """     

  # dictionary of skeletons by parent node id
  skels = {}

  # list of nodes in the swc file.
  nodes={}

  # comment in the swcfiles
  comments = []

  try:

    # number of ids to create.  do them all at once.
    idsneeded = 0

    # first pass of the file
    for line in swcfile:

      # find how many ids we need
      if not re.match ( '^#.*$', line ):

        # otherwise, parse the record according to SWC 
        # n T x y z R P
        ( swcnodeidstr, nodetype, xpos, ypos, zpos, radius, swcparentidstr )  = line.split()
        swcnodeid = int(swcnodeidstr)
        swcparentid = int(swcparentidstr)

        if swcparentid == -1:
          idsneeded += 2
        else:
          idsneeded += 1

    # reserve ids
    lowid = db.reserve ( ch, idsneeded )

    # reset file pointer for second pass
    swcfile.seek(0)

    # second pass to ingest the field
    for line in swcfile:
  
      # Store comments as KV 
      if re.match ( '^#.*$', line ):
        comments.append(line)
      else:

        # otherwise, parse the record according to SWC 
        # n T x y z R P
        ( swcnodeidstr, nodetype, xpos, ypos, zpos, radius, swcparentidstr )  = line.split()
        swcnodeid = int(swcnodeidstr)
        swcparentid = int(swcparentidstr)

        # create a node
        node = annotation.AnnNode( db ) 

        node.setField ( 'annid', lowid )
        lowid += 1
        node.setField ( 'nodetype', nodetype )
        node.setField ( 'location', (xpos,ypos,zpos) )
        node.setField ( 'radius', radius )
        if swcparentid == -1:
          node.setField ( 'parentid', -1 )
        else:
          node.setField ( 'parentid', nodes[swcparentid].getField('annid'))

        nodes[swcnodeid] = node

        # if it's a root node create a new skeleton
        if swcparentid == -1: 

          # Create a skeleton
          skels[swcnodeid] = annotation.AnnSkeleton ( db )

          # assign an identifier
          skels[swcnodeid].setField('annid', lowid)

          # assign sekeleton id for the node
          node.setField ( 'skeletonid', lowid )

          # increment the id
          lowid += 1

        else:

          # set to skelton id of parent
          node.setField ( 'skeletonid', nodes[swcparentid].getField('skeletonid') )

  except Exception, e:
    import pdb; pdb.set_trace()
    raise

  print "Build all skeletons, Starting DB txn."

  import pdb; pdb.set_trace()

  # having parsed the whole file, send to DB in a transaction
  db.startTxn()
  cursor = db.getCursor()

  # store the skeletons
  for (skelid, skel) in skels.iteritems():

    # add comments to each skeleton KV pair
    commentno = 0
    for comment in comments:
      skel.kvpairs[commentno] = comment
      commentno += 1

    skel.store( ch, cursor )

  import pdb; pdb.set_trace()

  # store the nodes
  for (nodeid,node) in nodes.iteritems():
    node.store( ch, cursor )

  db.commit()

  return [ x.annid for (i,x) in skels.iteritems() ]


def querySWC ( swcfile, ch, db, proj, skelids=None ):
  """Query the list of skelids (skeletons) and populate an open file swcfile
     with lines of swc data."""

  try:

    cursor = db.getCursor()
    db.startTxn()

    # write out metadata about where this came from
    # OCP version number and schema number
    f.write('# OCP (Open Connectome Project) Version {} Schema {}'.format(proj.getOCPVersion(),proj.getSchemaVersion()))
    # OCP project and channel
    f.write('# Project {} Channel {}'.format(proj.getProjectName(),ch.getChannelName()))

    # get a skeleton for metadata and populate the comments field
    if skelids != None and len(skelids)==0:

      skel == annotation.Skeleton( db )
      skel.retrieve ( ch, skelids[0], cursor )

      # write each key value line out as a comment
      for (k,v) in skel.getKVPairs():
        # match a comment
        if re.match ( "^#.*", v ):
          fwrite(v)
        else:
          fwrite("# {} {}".format(k,v))
      
    nodegen = db.queryNodes ( skelids )
    # iterate over all nodes
    for node in nodegen: 
      skeletonid = node.getField ( 'skeletonid' )
      annid = node.getField ( 'annid' ) 
      nodetype = node.getField ( 'nodetype')
      (xpos,ypos,zpos) = node.getField ( 'location')
      radius = node.getField ( 'radius')
      parentid = node.getField ( 'parentid')

    # write an node in swc
    # n T x y z R P
#    fwrite ( "{} {} {} {} {} {} {} {}".format ( annid, nodetype,  ,,,,, parentid ))

    db.commit()

  finally:
    db.closeCursor()

