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

  parser = argparse.ArgumentParser(description='Create a new dataset.')
  parser.add_argument('dsname', action="store", help='Name of the dataset')
  parser.add_argument('ximagesize', type=int, action="store")
  parser.add_argument('yimagesize', type=int, action="store")
  parser.add_argument('startslice', type=int, action="store")
  parser.add_argument('endslice', type=int, action="store")
  parser.add_argument('zoomlevels', type=int, action="store")
  parser.add_argument('zscale', type=float, action="store", help='Relative resolution between x,y and z')
  parser.add_argument('description', action="store", help='Description of the dataset')
  result = parser.parse_args()

  # Get database info
  pd = ocpcaproj.OCPCAProjectsDB()

  pd.newDataset ( result.dsname, result.ximagesize, result.yimagesize, result.startslice, result.endslice, result.zoomlevels, result.zscale, result.description
                  )
  ds = pd.loadDatasetConfig(result.dsname)
  print ds.dataset_name + "created successfully"
  

if __name__ == "__main__":
  main()


  
