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

import django.http
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.template import Context
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.forms.models import inlineformset_factory
import django.forms


import ocpcaprivate
import ocpcarest
import ocpcaproj
import string
import random
import MySQLdb

from models import Project
from models import Dataset
from models import Token
from forms import CreateProjectForm
from forms import CreateDatasetForm
from forms import CreateTokenForm
from forms import dataUserForm

from django.core.urlresolvers import get_script_prefix
import os
import subprocess
from ocpcaerror import OCPCAError

import logging
logger=logging.getLogger("ocp")

# Helpers

''' Base url just redirects to welcome'''
def default(request):
  return redirect(get_script_prefix()+'profile', {"user":request.user})

''' Little welcome message'''
@login_required(login_url='/ocp/accounts/login/')
def profile(request):

  try:
    if request.method == 'POST':
      if 'filter' in request.POST:
        #FILTER PROJECTS BASED ON INPUT VALUE
        userid = request.user.id
        filteroption = request.POST.get('filteroption')
        filtervalue = (request.POST.get('filtervalue')).strip()
        
        pd = ocpcaproj.OCPCAProjectsDB()

        # get the visible data sets
        if request.user.is_superuser:
          visible_datasets=Dataset.objects.all()
        else:
          visible_datasets=Dataset.objects.filter(user_id=userid) | Dataset.objects.filter(public=1)

        projs = defaultdict(list)

        dbs = defaultdict(list)
        for db in visible_datasets:
          proj = Project.objects.filter(dataset_id=db.dataset_name, user_id=userid) | Project.objects.filter(dataset_id=db.dataset_name, public=1)
          if proj:
            dbs[db.dataset_name].append(proj)
          else:
            dbs[db.dataset_name].append(None)

        if request.user.is_superuser:
          visible_projects = Project.objects.all()
        else:
          visible_projects = Project.objects.filter(user_id=userid) | Project.objects.filter(public=1) 

        return render_to_response('profile.html', { 'databases': dbs.iteritems() ,'projects': visible_projects.values_list(flat=True) },context_instance=RequestContext(request))

      elif 'delete_data' in request.POST:

        pd = ocpcaproj.OCPCAProjectsDB()
        username = request.user.username
        project_to_delete = (request.POST.get('project_name')).strip()
                
        reftokens = Token.objects.filter(project_id=project_to_delete)
        if reftokens:
          messages.error(request, 'Project cannot be deleted. Please delete all tokens for this project first.')
          return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')
        else:
          proj = Project.objects.get(project_name=project_to_delete)
          if proj:
            if proj.user_id == request.user.id or request.user.is_superuser:
              #Delete project from the table followed  by the database.
              # deleting a project is super dangerous b/c you may delete it out from other tokens.
              #  on other servers.  So, only delete when it's on the same server for now
              pd.deleteOCPCADB(project_to_delete)
              proj.delete()          
              messages.success(request,"Project deleted")
            else:
              messages.error(request,"Cannot delete.  You are not owner of this project or not superuser.")
          else:
            messages.error( request,"Project not found.")
          return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')

      elif 'delete' in request.POST:
        pd = ocpcaproj.OCPCAProjectsDB()
        username = request.user.username
        project_to_delete = (request.POST.get('project_name')).strip()
                
        reftokens = Token.objects.filter(project_id=project_to_delete)
        if reftokens:
          messages.error(request, 'Project cannot be deleted. Please delete all tokens for this project first.')
          return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')
        else:
          proj = Project.objects.get(project_name=project_to_delete)
          if proj:
            if proj.user_id == request.user.id or request.user.is_superuser:
              #Delete project from the table followed  by the database.
              # RBTODO deleting a project is super dangerous b/c you may delete it out from other tokens.
              #  on other servers.  So, only delete when it's on the same server for now
              #if proj.getKVServer()==proj.getDBHost():
              #   pd.deleteOCPCADB(project_to_delete)
              proj.delete()          
              messages.success(request,"Project deleted")
            else:
              messages.error(request,"Cannot delete.  You are not owner of this project or not superuser.")
          else:
            messages.error( request,"Project not found.")
          return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')
      
      elif 'info' in request.POST:
      #GET PROJECT INFO -----------TODO
        token = (request.POST.get('roptions')).strip()
        return HttpResponse(ocpcarest.projInfo(token), content_type="product/hdf5" )
      
      elif 'update' in request.POST:
        project_to_update =(request.POST.get('project_name')).strip() 
        request.session["project_name"] = project_to_update
        return redirect(updateproject)
      
      elif 'tokens' in request.POST:
        projname=(request.POST.get('project_name')).strip()
        request.session["project"] = projname
        return redirect(get_tokens)

      elif 'backup' in request.POST:
        path = ocpcaprivate.backuppath + '/' + request.user.username
        if not os.path.exists(path):
          os.mkdir( path, 0755 )
        # Get the database information
        pd = ocpcaproj.OCPCAProjectsDB()
        db = (request.POST.get('project_name')).strip()
        ofile = path +'/'+ db +'.sql'
        outputfile = open(ofile, 'w')
        dbuser =ocpcaprivate.dbuser
        passwd =ocpcaprivate.dbpasswd

        p = subprocess.Popen(['mysqldump', '-u'+ dbuser, '-p'+ passwd, '--single-transaction', '--opt', db], stdout=outputfile).communicate(None)
        messages.success(request, 'Sucessfully backed up database '+ db)
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')

      else:
        # Invalid POST
        messages.error(request,"Unrecognized POST")
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')

    else:
    # GET Projects
      userid = request.user.id

      # get the visible data sets
      if request.user.is_superuser:
        visible_datasets=Dataset.objects.all()
      else:
        visible_datasets=Dataset.objects.filter(user_id=userid) | Dataset.objects.filter(public=1)

      dbs = defaultdict(list)
      for db in visible_datasets:
        proj = Project.objects.filter(dataset_id=db.dataset_name, user_id=userid) | Project.objects.filter(dataset_id=db.dataset_name, public=1)
        if proj:
          dbs[db.dataset_name].append(proj)
        else:
          dbs[db.dataset_name].append(None)
      
      if request.user.is_superuser:
        visible_projects = Project.objects.all()
      else:
        visible_projects = Project.objects.filter(user_id=userid) | Project.objects.filter(public=1) 

      return render_to_response('profile.html', { 'databases': dbs.iteritems() ,'projects':visible_projects },context_instance=RequestContext(request))
    
  except OCPCAError, e:

    messages.error("Unknown exception in administrative interface = {}".format(e)) 

    # GET Projects
    username = request.user.username
    all_datasets= Dataset.objects.all()
    dbs = defaultdict(list)
    for db in all_datasets:
      proj = Project.objects.filter(dataset_id=db.dataset_name, user_id = request.user)
      if proj:
        dbs[db.dataset_name].append(proj)
      else:
        dbs[db.dataset_name].append(None)
    
    all_projects = Project.objects.values_list('project_name',flat= True)
    return render_to_response('profile.html', { 'databases': dbs.iteritems() ,'projects':all_projects },context_instance=RequestContext(request))
    

@login_required(login_url='/ocp/accounts/login/')
def get_datasets(request):

  try:

    pd = ocpcaproj.OCPCAProjectsDB()

    userid = request.user.id
    if request.user.is_superuser:
      visible_datasets=Dataset.objects.all()
    else:
      visible_datasets= Dataset.objects.filter(user_id=userid) | Dataset.objects.filter(public=1)

    if request.method == 'POST':

      if 'filter' in request.POST:
        filtervalue = (request.POST.get('filtervalue')).strip()
        visible_datasets = visible_datasets.filter(dataset_name=filtervalue)
        return render_to_response('datasets.html', { 'dts': visible_datasets },context_instance=RequestContext(request))

      elif 'delete' in request.POST:

        #delete specified dataset
        ds = (request.POST.get('dataset_name')).strip()
        ds_to_delete = Dataset.objects.get(dataset_name=ds)
        
        # Check for projects with that dataset
        proj = Project.objects.filter(dataset_id=ds_to_delete.dataset_name)
        if proj:
          messages.error(request, 'Dataset cannot be deleted. Please delete all projects for this dataset first.')
        else:
          if ds_to_delete.user_id == request.user.id or request.user.is_superuser:
            ds_to_delete.delete()
            messages.success(request, 'Deleted Dataset ' + ds)
          else:
            messages.error(request,"Cannot delete.  You are not owner of this dataset or not superuser.")

          # refresh to remove deleted
          if request.user.is_superuser:
            visible_datasets=Dataset.objects.all()
          else:
            visible_datasets=Dataset.objects.filter(user=request.user.id) | Dataset.objects.filter(public=1)

        return render_to_response('datasets.html', { 'dts': visible_datasets },context_instance=RequestContext(request))
      elif 'update' in request.POST:
        ds = (request.POST.get('dataset_name')).strip()
        request.session["dataset_name"] = ds
        return redirect(updatedataset)

      else:
        #Load datasets
        return render_to_response('datasets.html', { 'dts': visible_datasets },context_instance=RequestContext(request))

    else:
      # GET datasets
      return render_to_response('datasets.html', { 'dts': visible_datasets },context_instance=RequestContext(request))

  except OCPCAError, e:
    messages.error("Unknown exception in administrative interface = {}".format(e)) 
    return render_to_response('datasets.html', { 'dts': visible_datasets },context_instance=RequestContext(request))    

@login_required(login_url='/ocp/accounts/login/')
def get_alltokens(request):

  if 'filter' in request.POST:
    del request.session['filter']
  if 'project' in request.session:
    del request.session['project']

  return get_tokens(request)

 

@login_required(login_url='/ocp/accounts/login/')
def get_tokens(request):

  username = request.user.username
  pd = ocpcaproj.OCPCAProjectsDB()  

  try:
    if request.method == 'POST':
      if 'filter' in request.POST:
      #Filter tokens based on an input value
        filteroption = request.POST.get('filteroption')
        filtervalue = (request.POST.get('filtervalue')).strip()
        all_tokens = Token.objects.filter(token_name=filtervalue)
        proj=""
        return render_to_response('token.html', { 'tokens': all_tokens, 'database': proj },context_instance=RequestContext(request))

      elif 'delete' in request.POST:
      #Delete the token from the token table
        token_to_delete = (request.POST.get('token')).strip()
        token = Token.objects.get(token_name=token_to_delete)
        if token:
          if token.user_id == request.user.id or request.user.is_superuser:
            token.delete()          
            messages.success(request,"Token deleted " + token_to_delete)
          else:
            messages.error(request,"Cannot delete.  You are not owner of this token or not superuser.")
        else:
          messages.error(request,"Unable to delete " + token_to_delete)
        return redirect(get_tokens)

      elif 'downloadtoken' in request.POST:
        #Download the token in a test file
        token = (request.POST.get('token')).strip()
        response = HttpResponse(token,content_type='text/html')
        response['Content-Disposition'] = 'attachment; filename="ocpca.token"'
        return response

      elif 'update' in request.POST:
      #update project token
        token = (request.POST.get('token')).strip()
        request.session["token_name"] = token
        return redirect(updatetoken)

      else:
        #Unrecognized Option
        messages.error("Invalid request")
        return redirect(get_tokens)

    else:
      # GET tokens for the specified project
      username = request.user.username
      if "project" in request.session:
        proj = request.session["project"]
        all_tokens = Token.objects.filter(project_id=proj)
      else:
        proj=""
        all_tokens = Token.objects.all()
      return render_to_response('token.html', { 'tokens': all_tokens, 'database': proj },context_instance=RequestContext(request))
    
  except OCPCAError, e:
    messages.error("Unknown exception in administrative interface = {}".format(e)) 
    datasets = pd.getDatasets()
    return render_to_response('datasets.html', { 'dts': datasets },context_instance=RequestContext(request))




@login_required(login_url='/ocp/accounts/login/')
def createproject(request):

  pd = ocpcaproj.OCPCAProjectsDB()  

  if request.method == 'POST':
    if 'createproject' in request.POST:

      form = CreateProjectForm(request.POST)

      # restrict datasets to user visible fields
      form.fields['dataset'].queryset = Dataset.objects.filter(user_id=request.user.id) | Dataset.objects.filter(public=1)

      if form.is_valid():
        new_project=form.save(commit=False)
        new_project.user_id=request.user.id
        new_project.save()
        try:
          # create a database when not linking to an existing databases
          if not request.POST.get('nocreate') == 'on':
            pd.newOCPCADB( new_project.project_name )
          if 'token' in request.POST:
            tk = Token ( token_name = new_project.project_name, token_description = 'Default token for public project', project_id=new_project, readonly = 0, user_id=request.user.id, public=new_project.public ) 
            tk.save()
        except Exception, e:
          logger.error("Failed to create project.  Error {}".format(e))
          new_project.delete()

        return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile/')
      else:
        context = {'form': form}
        print form.errors
        return render_to_response('createproject.html',context,context_instance=RequestContext(request))

    else:
      #default
      return redirect(profile)
  else:
    '''Show the Create Project form'''

    form = CreateProjectForm()

    # restrict datasets to user visible fields
    form.fields['dataset'].queryset = Dataset.objects.filter(user_id=request.user.id) | Dataset.objects.filter(public=1)

    context = {'form': form}
    return render_to_response('createproject.html',context,context_instance=RequestContext(request))
      
@login_required(login_url='/ocp/accounts/login/')
def createdataset(request):
 
  if request.method == 'POST':
    if 'createdataset' in request.POST:
      form = CreateDatasetForm(request.POST)
      if form.is_valid():
        new_dataset=form.save(commit=False)
        new_dataset.user_id=request.user.id
        new_dataset.save()
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/datasets')
      else:
        context = {'form': form}
        print form.errors
        return render_to_response('createdataset.html',context,context_instance=RequestContext(request))
    else:
      #default
      return redirect(datasets)
  else:
    '''Show the Create datasets form'''
    form = CreateDatasetForm()
    context = {'form': form}
    return render_to_response('createdataset.html',context,context_instance=RequestContext(request))


@login_required(login_url='/ocp/accounts/login/')
def updatedataset(request):

  # Get the dataset to update
  ds = request.session["dataset_name"]
  if request.method == 'POST':
    if 'UpdateDataset' in request.POST:
      ds_update = get_object_or_404(Dataset,dataset_name=ds)
      form = CreateDatasetForm(data= request.POST or None,instance=ds_update)
      if form.is_valid():
        form.save()
        messages.success(request, 'Sucessfully updated dataset')
        del request.session["dataset_name"]
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/datasets')
      else:
        #Invalid form
        context = {'form': form}
        print form.errors
        return render_to_response('updatedataset.html',context,context_instance=RequestContext(request))
    else:
      #unrecognized option
      return HttpResponseRedirect(get_script_prefix()+'ocpuser/datasets')
  else:
    print "Getting the update form"
    if "dataset_name" in request.session:
      ds = request.session["dataset_name"]
    else:
      ds = ""
    ds_to_update = Dataset.objects.filter(dataset_name=ds)
    data = {
      'dataset_name': ds_to_update[0].dataset_name,
      'ximagesize':ds_to_update[0].ximagesize,
      'yimagesize':ds_to_update[0].yimagesize,
      'zimagesize':ds_to_update[0].zimagesize,
      'xoffset':ds_to_update[0].xoffset,
      'yoffset':ds_to_update[0].yoffset,
      'zoffset':ds_to_update[0].zoffset,
      'xvoxelres':ds_to_update[0].xvoxelres,
      'yvoxelres':ds_to_update[0].yvoxelres,
      'zvoxelres':ds_to_update[0].zvoxelres,
      'scalinglevels':ds_to_update[0].scalinglevels,
      'scalingoption':ds_to_update[0].scalingoption,
      'startwindow':ds_to_update[0].startwindow,
      'endwindow':ds_to_update[0].endwindow,
      'starttime':ds_to_update[0].starttime,
      'endtime':ds_to_update[0].endtime,
      'dataset_description':ds_to_update[0].dataset_description,
            }
    form = CreateDatasetForm(initial=data)
    context = {'form': form}
    return render_to_response('updatedataset.html',context,context_instance=RequestContext(request))

@login_required(login_url='/ocp/accounts/login/')
def updatetoken(request):

  # Get the dataset to update
  token = request.session["token_name"]
  if request.method == 'POST':
    if 'UpdateToken' in request.POST:
      token_update = get_object_or_404(Token,token_name=token)
      form = CreateTokenForm(data=request.POST or None, instance=token_update)
      if form.is_valid():
        newtoken = form.save( commit=False )
        if newtoken.user_id == request.user.id or request.user.is_superuser:
          # if you changed the token name, delete old token
          newtoken.save()
          if newtoken.token_name != token:
            deltoken = Token.objects.filter(token_name=token)
            deltoken.delete()
          messages.success(request, 'Sucessfully updated Token')
          del request.session["token_name"]
        else:
          messages.error(request,"Cannot update.  You are not owner of this token or not superuser.")
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/token')
      else:
        #Invalid form
        context = {'form': form}
        print form.errors
        return render_to_response('updatetoken.html',context,context_instance=RequestContext(request))
    else:
      #unrecognized option
      return HttpResponseRedirect(get_script_prefix()+'ocpuser/token')
  else:
    print "Getting the update form"
    if "token_name" in request.session:
      token = request.session["token_name"]
    else:
      token = ""
    token_to_update = Token.objects.filter(token_name=token)
    data = {
      'token_name': token_to_update[0].token_name,
      'token_description':token_to_update[0].token_description,
      'project':token_to_update[0].project_id,
      'readonly':token_to_update[0].readonly,
      'public':token_to_update[0].public,
      
            }
    form = CreateTokenForm(initial=data)
    context = {'form': form}
    return render_to_response('updatetoken.html',context,context_instance=RequestContext(request))

@login_required(login_url='/ocp/accounts/login/')
def updateproject(request):

  proj_name = request.session["project_name"]
  if request.method == 'POST':
    
    if 'UpdateProject' in request.POST:
      proj_update = get_object_or_404(Project,project_name=proj_name)
      form = CreateProjectForm(data= request.POST or None,instance=proj_update)
      if form.is_valid():
        newproj = form.save(commit=False)
        if newproj.user_id == request.user.id or request.user.is_superuser:
          if newproj.project_name != proj_name:
            messages.error ("Cannot change the project name.  MySQL cannot rename databases.")
          else:
            newproj.save()
            messages.success(request, 'Sucessfully updated project ' + proj_name)
        else:
          messages.error(request,"Cannot update.  You are not owner of this project or not superuser.")
        del request.session["project_name"]
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')
      else:
        #Invalid form
        context = {'form': form}
        return render_to_response('updateproject.html',context,context_instance=RequestContext(request))
    else:
      #unrecognized option
      messages.error(request,"Unrecognized Post")
      return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')
      
  else:
    #Get: Retrieve project and display update project form.
    if "project_name" in request.session:
      proj = request.session["project_name"]
    else:
      proj = ""
    project_to_update = Project.objects.filter(project_name=proj)
    data = {
      'project_name': project_to_update[0].project_name,
      'project_description':project_to_update[0].project_description,
      'dataset':project_to_update[0].dataset_id,
      'datatype':project_to_update[0].datatype,
      'overlayproject':project_to_update[0].overlayproject,
      'overlayserver':project_to_update[0].overlayserver,
      'resolution':project_to_update[0].resolution,
      'exceptions':project_to_update[0].exceptions,
      'host':project_to_update[0].host,
      'kvengine':project_to_update[0].kvengine,
      'kvserver':project_to_update[0].kvserver,
      'propagate':project_to_update[0].propagate,
    }
    form = CreateProjectForm(initial=data)
    context = {'form': form}
    return render_to_response('updateproject.html',context,context_instance=RequestContext(request))


@login_required(login_url='/ocp/accounts/login/')
def createtoken(request):

  if request.method == 'POST':
    if 'createtoken' in request.POST:

      form = CreateTokenForm(request.POST)

      # restrict projects to user visible fields
      form.fields['project'].queryset = Project.objects.filter(user_id=request.user.id) | Project.objects.filter(public=1)

      if form.is_valid():
        new_token=form.save(commit=False)
        new_token.user_id=request.user.id
        new_token.save()
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')
      else:
        context = {'form': form}
        print form.errors
        return render_to_response('createtoken.html',context,context_instance=RequestContext(request))
    else:
      #default                                                                                                                                                          
      return redirect(profile)
  else:
    '''Show the Create datasets form'''
    form = CreateTokenForm()

    # restrict projects to user visible fields
    form.fields['project'].queryset = Project.objects.filter(user_id=request.user.id) | Project.objects.filter(public=1)

    context = {'form': form}
    return render_to_response('createtoken.html',context,context_instance=RequestContext(request))
      
@login_required(login_url='/ocp/accounts/login/')
def restoreproject(request):
  if request.method == 'POST':
   
    if 'RestoreProject' in request.POST:
      form = CreateProjectForm(request.POST)
      if form.is_valid():
        project = form.cleaned_data['project_name']
        description = form.cleaned_data['project_description']        
        dataset = form.cleaned_data['dataset']
        datatype = form.cleaned_data['datatype']
        overlayproject = form.cleaned_data['overlayproject']
        overlayserver = form.cleaned_data['overlayserver']
        resolution = form.cleaned_data['resolution']
        exceptions = form.cleaned_data['exceptions']        
        dbhost = form.cleaned_data['host']        
        kvengine=form.cleaned_data['kvengine']
        kvserver=form.cleaned_data['kvserver']
        propagate =form.cleaned_data['propagate']
        username = request.user.username
        nocreateoption = request.POST.get('nocreate')
        if nocreateoption =="on":
          nocreate = 1
        else:
          nocreate = 0
        new_project= form.save(commit=False)
        new_project.user = request.user
        new_project.save()
        # Get database info
        pd = ocpcaproj.OCPCAProjectsDB()
        
        bkupfile = request.POST.get('backupfile')
        path = ocpcaprivate.backuppath+ '/'+ request.user.username + '/' + bkupfile
        if os.path.exists(path):
          print "File exists"
        else:
          #TODO - Return error
          print "Error"
        proj=pd.loadProjectDB(project)
        
        
        #Create the database
        newconn = MySQLdb.connect (host = dbhost, user = ocpcaprivate.dbuser, passwd = ocpcaprivate.dbpasswd, db=ocpcaprivate.db )
        newcursor = newconn.cursor()
        
        try:
          sql = "Create database " + project  
          newcursor.execute(sql)
        except Exception:
          print("Database already exists")
          
          
      # close connection just to be sure
        newcursor.close()
        dbuser = ocpcaprivate.dbuser
        passwd = ocpcaprivate.dbpasswd
      
        proc = subprocess.Popen(["mysql", "--user=%s" % dbuser, "--password=%s" % passwd, project],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        proc.communicate(file(path).read())
        messages.success(request, 'Sucessfully restored database '+ project)
        return redirect(profile)
    
      else:
        #Invalid Form
        context = {'form': form}
        print form.errors
        return render_to_response('profile.html',context,context_instance=RequestContext(request))
    else:
      #Invalid post - redirect to profile for now
      return redirect(profile)
  else:        
      #GET DATA
    randtoken = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(64))
    form = CreateProjectForm(initial={'token': randtoken})
    path = ocpcaprivate.backuppath +'/'+ request.user.username
    if os.path.exists(path):
      file_list =os.listdir(path)   
    else:
      file_list={}
    context = Context({'form': form, 'flist': file_list})
    return render_to_response('restoreproject.html',context,context_instance=RequestContext(request))


def downloaddata(request):
  
  try:
    pd = ocpcaproj.OCPCAProjectsDB()
    
    if request.method == 'POST':
      form= dataUserForm(request.POST)
      if form.is_valid():
        curtoken=request.POST.get('token')
        if curtoken=="other":
          curtoken=request.POST.get('other')
          
        format = form.cleaned_data['format']
        resolution = form.cleaned_data['resolution']
        xmin=form.cleaned_data['xmin']
        xmax=form.cleaned_data['xmax']
        ymin=form.cleaned_data['ymin']
        ymax=form.cleaned_data['ymax']
        zmin=form.cleaned_data['zmin']
        zmax=form.cleaned_data['zmax']
        webargs= curtoken+"/"+format+"/"+str(resolution)+"/"+str(xmin)+","+str(xmax)+"/"+str(ymin)+","+str(ymax)+"/"+str(zmin)+","+str(zmax)+"/"
          
        if format=='hdf5':
          return django.http.HttpResponse(ocpcarest.getCutout(webargs), content_type="product/hdf5" )
        elif format=='npz':
          return django.http.HttpResponse(ocpcarest.getCutout(webargs), content_type="product/npz" )
        else:
          return django.http.HttpResponse(ocpcarest.getCutout(webargs), content_type="product/zip" )
          
      else:
        return redirect(downloaddata)
        #return render_to_response('download.html',context_instance=RequestContext(request))
    else:
      # Load Download page with public tokens                                           
      pd = ocpcaproj.OCPCAProjectsDB()
      form = dataUserForm()
      tokens = pd.getPublic ()
      context = {'form': form ,'publictokens': tokens}
      return render_to_response('download.html',context,context_instance=RequestContext(request))
      #return render_to_response('download.html', { 'dts': datasets },context_instance=\
          #         RequestContext(request))                                                                
  except OCPCAError, e:
    messages.error("Unknown exception in administrative interface = {}".format(e)) 
    tokens = pd.getPublic ()
    return redirect(downloaddata)
