import argparse

import sys
import os
sys.path += [os.path.abspath('../django')]

import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcarest
import ocpcaproj

def main():
# 
  parser = argparse.ArgumentParser(description='Create a new annotation project.')
  parser.add_argument('token', action="store")
  parser.add_argument('openid', action="store")
  parser.add_argument('host', action="store")
  parser.add_argument('project', action="store")
  parser.add_argument('projectdescription', action="store")
  parser.add_argument('datatype', action="store", type=int, help='1 8-bit data or 2 32-bit annotations' )
  parser.add_argument('dataset', action="store")
  parser.add_argument('dataurl', action="store")
  parser.add_argument('--readonly', action='store_true', help='Project is readonly')
  parser.add_argument('--noexceptions', action='store_true', help='Project has no exceptions.  (FASTER).')
  parser.add_argument('--nocreate', action='store_true', help='Do not create a database.  Just make a project entry.')
  parser.add_argument('--resolution', action='store',type=int, help='Maximum resolution for an annotation projects', default=0)

  result = parser.parse_args()

  # Get database info
  pd = ocpcaproj.OCPCAProjectsDB()
  # Check if the dataset is valid
  ds = pd.loadDatasetConfig(result.dataset)
  print ds.dataset_name
  print ds.dataset_id

  pd.newOCPCAProj( result.project, result.projectdescription,result.dataset,result.datatype,result.resolution,result.exceptions, result.host,result.nocreate,result.openid)

  

if __name__ == "__main__":
  main()


  
