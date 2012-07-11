import empaths
import MySQLdb

import annprivate
import dbconfig

#
#  AnnotateCube: manipulate the in-memory data representation of the 3-d cube of data
#    that contains annotations.  
#


#
# Annotation project not found
#
class AnnoProjException (Exception):
  """Could not load and annotation project"""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


class AnnotateProject:
  """Project specific annotation data"""

  # Constructor 
  def __init__(self, dbname, dbhost, dataset, resolution ):
    """Initialize the Annotation Project"""
    
    self._dbhost = dbhost
    self._dbname = dbname
    self._dataset = dataset
    self._resolution = resolution

    # Could add these to dbconfig.  Probably remove res as tablebase instead
    self._ids_tbl = "ids"


  # Accessors
  def getDBHost ( self ):
    return self._dbhost
  def getDBName ( self ):
    return self._dbname
  def getDataset ( self ):
    return self._dataset
  def getResolution ( self ):
    return self._resolution
  def getIDsTbl ( self ):
    return self._ids_tbl
  def getEntitiesTbl ( self ):
    return self._entities_tbl

  # accessors for RB to fix
  def getDBUser( self ):
    return annprivate.dbuser
  def getDBPasswd( self ):
    return annprivate.dbpasswd

  def getTable ( self, resolution ):
    """Return the appropriate table for the specified resolution"""
    return "res"+str(resolution)
  
  def getIdxTable ( self, resolution ):
    """Return the appropriate Index table for the specified resolution"""
    return "idx"+str(resolution)

class AnnotateProjectsDB:
  """Database for the annotation projects"""

  def __init__(self):
    """Create the database connection"""

    # Connection info in dbconfig
    self.conn = MySQLdb.connect (host = annprivate.dbhost,
                          user = annprivate.dbuser,
                          passwd = annprivate.dbpasswd,
                          db = annprivate.db )

  #
  # Load the annotation databse information based on the token
  #
  def getAnnoProj ( self, token ):
    """Load the annotation database information based on the token"""


    # Lookup the information for the database project based on the token
    sql = "SELECT * from %s where token = \'%s\'" % (annprivate.table, token)

    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Could not query annotations projects database"
      raise AnnoProjException ( "Annotation Project Database error" )

    # get the project information 
    row = cursor.fetchone()

    # if the project is not found.  error
    if ( row == None ):
      print "No project found"
      raise AnnoProjException ( "Project token not found" )

    [token, openid, host, project, dataset, resolution ] = row

    return AnnotateProject ( project, host, dataset, resolution )


  #
  # Load the annotation databse information based on the token
  #
  def newAnnoProj ( self, token, openid, dbhost, project, dataset, resolution ):
    """Create a new annotation project"""

    dbcfg = dbconfig.switchDataset ( dataset )

    print dbhost, project

    # Insert the project entry into the database
    sql = "INSERT INTO {0} VALUES ( \'{1}\', \'{2}\', \'{3}\', \'{4}\', \'{5}\', {6}  )".format (\
        annprivate.table, token, openid, dbhost, project, dataset, resolution )

    print sql

    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Failed to create new project", e
      raise AnnoProjException ( "Failed to create new project" )

    # Make the database and associated annotation tables
    sql = "CREATE DATABASE %s;" % project
    print "Executing: ", sql
   
    try:
      cursor = self.conn.cursor()
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Failed to create database for new project", e
      raise AnnoProjException ( "Failed to create database for new project" )

    self.conn.commit()

    # Connect to the new database
    newconn = MySQLdb.connect (host = dbhost,
                          user = annprivate.dbuser,
                          passwd = annprivate.dbpasswd,
                          db = project )

    newcursor = newconn.cursor()

    sql = "CREATE TABLE ids ( id BIGINT PRIMARY KEY);\n"

    # And the RAMON objects
    sql += "CREATE TABLE annotations (annoid BIGINT PRIMARY KEY, anno_type INT, confidence FLOAT, status INT);"
    sql += "CREATE TABLE seeds (annoid BIGINT PRIMARY KEY, parentid BIGINT, sourceid BIGINT, cube_location INT, positionx INT, positiony INT, positionz INT);"
    sql += "CREATE TABLE synapses (annoid BIGINT PRIMARY KEY, synapse_type INT, weight FLOAT);"
    sql += "CREATE TABLE kvpairs ( annoid BIGINT, kv_key VARCHAR(255), kv_value VARCHAR(255), PRIMARY KEY ( annoid, kv_key ));"

    for i in dbcfg.resolutions: 
      sql += "CREATE TABLE res%s ( zindex BIGINT PRIMARY KEY, cube LONGBLOB );\n" % i
      sql += "CREATE TABLE idx%s ( annid BIGINT PRIMARY KEY, cube LONGBLOB );\n" % i

    print sql

    try:
      cursor = newconn.cursor()
      newcursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Failed to create tables for new project", e
      raise AnnoProjException ( "Failed to create database for new project" )