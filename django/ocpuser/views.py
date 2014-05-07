import django.http
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404 
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import get_script_prefix
from django.template import Context
from collections import defaultdict
from django.contrib import messages
from django.forms.models import inlineformset_factory
import ocpcarest
import ocpcaproj
import string
import random

from models import Project
from models import Dataset
from models import Token

from forms import CreateProjectForm
from forms import ProjectFormSet
from forms import CreateDatasetForm
from forms import UpdateProjectForm

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
        openid = request.user.username
        filteroption = request.POST.get('filteroption')
        filtervalue = (request.POST.get('filtervalue')).strip()
        pd = ocpcaproj.OCPCAProjectsDB()
        projects = pd.getFilteredProjects ( openid,filteroption,filtervalue )
        
        databases = pd.getDatabases ( openid)
        dbs = defaultdict(list)
        for db in databases:
          proj = pd.getFilteredProjs(openid,filteroption,filtervalue,db[0]);
          dbs[db].append(proj)
          
        return render_to_response('profile.html', { 'projs': projects,'databases': dbs.iteritems() },
                                context_instance=RequestContext(request))
      elif 'delete' in request.POST:
      #DELETE PROJECT WITH SPECIFIED TOKEN

        pd = ocpcaproj.OCPCAProjectsDB()
        openid = request.user.username
        
        project = (request.POST.get('projname')).strip()
        print " Ready to delete " ,project
      #token = (request.POST.get('token')).strip()
       
        pd.deleteOCPCADatabase(project)
        # pd.deleteTokenDescription(token)
        #return redirect(profile)
      elif 'downloadtoken' in request.POST:
      #DOWNLOAD TOKEN FILE
        #      token = (request.POST.get('token')).strip()
        token = (request.POST.get('roptions')).strip()
        print token
        response = HttpResponse(token,content_type='text/html')
        response['Content-Disposition'] = 'attachment; filename="ocpca.token"'
        return response
      elif 'info' in request.POST:
      #GET PROJECT INFO -----------TODO
        token = (request.POST.get('roptions')).strip()
      #token = (request.POST.get('token')).strip()+"/projinfo/test"
        return HttpResponse(ocpcarest.projInfo(token), mimetype="product/hdf5" )
      elif 'update' in request.POST:
      #UPDATE PROJECT TOKEN -- FOLOWUP
      #token = (request.POST.get('token')).strip()
        token = (request.POST.get('roptions')).strip()
        print token
        request.session["token"] = token
        return redirect(updateproject)
      elif 'tokens' in request.POST:
      #View token for the project        
        #import pdb;pdb.set_trace();
        print "in view tokens"
        projname = (request.POST.get('projname')).strip()
        print projname
        request.session["project"] = projname
        #return render_to_response('token.html',
       # projname,
        #                  context_instance=RequestContext(request))
        return redirect(tokens)

      elif 'backup' in request.POST:
      #BACKUP DATABASE
        path = '/data/scratch/ocpbackup/'+ request.user.username
        if not os.path.exists(path):
          os.mkdir( path, 0755 )
              #subprocess.call('whoami')
      # Get the database information
        pd = ocpcaproj.OCPCAProjectsDB()
        db = (request.POST.get('projname')).strip()
              #Open backupfile
        ofile = path +'/'+ db +'.sql'
        outputfile = open(ofile, 'w')
        p = subprocess.Popen(['mysqldump', '-ubrain', '-p88brain88', '--single-transaction', '--opt', db], stdout=outputfile).communicate(None)
         # return redirect(profile)
        messages.success(request, 'Sucessfully backed up database '+ db)
        return redirect(profile)
      else:
        # Invalid POST
        #
        pd = ocpcaproj.OCPCAProjectsDB()
        openid = request.user.username
# projects = pd.getProjects ( openid )
        projects = pd.getFilteredProjects ( openid ,"","")
        databases = pd.getDatabases ( openid)
        dbs = defaultdict(list)
        for db in databases:
          proj = pd.getFilteredProjs(openid,"","",db[0]);
          dbs[db].append(proj)
        return render_to_response('profile.html', { 'projs': projects, 'databases': dbs.iteritems() },context_instance=RequestContext(request))

    else:
    # GET Option
      #import pdb;pdb.set_trace()
      pd = ocpcaproj.OCPCAProjectsDB()
      openid = request.user.username
      databases = pd.getDatabases ( openid)
      dbs = defaultdict(list)
      for db in databases:
        proj = pd.getFilteredProjs(openid,"","",db[0]);
        dbs[db].append(proj)
        
      return render_to_response('profile.html', { 'databases': dbs.iteritems() },context_instance=RequestContext(request))
    
  except OCPCAError, e:
    #import pdb;pdb.set_trace();
    messages.error(request, e.value)
    pd = ocpcaproj.OCPCAProjectsDB()
    openid = request.user.username
    projects = pd.getFilteredProjects ( openid ,"","")
    databases = pd.getDatabases ( openid)
    dbs = defaultdict(list)
    for db in databases:
      proj = pd.getFilteredProjs(openid,"","",db[0]);
      dbs[db].append(proj)
      
    return render_to_response('profile.html', { 'projs': projects, 'databases': dbs.iteritems() },context_instance=RequestContext(request))
    




  #return render_to_response('datasets.html')


@login_required(login_url='/ocp/accounts/login/')
def tokens(request):
  pd = ocpcaproj.OCPCAProjectsDB()  
  #import pdb;pdb.set_trace();
  try:
    if request.method == 'POST':
      if 'filter' in request.POST:
      #FILTER PROJECTS BASED ON INPUT VALUE
        openid = request.user.username
        filteroption = request.POST.get('filteroption')
        filtervalue = (request.POST.get('filtervalue')).strip()
        pd = ocpcaproj.OCPCAProjectsDB()
        projects = pd.getFilteredProjects ( openid,filteroption,filtervalue )
        return render_to_response('token.html', { 'tokens': projects},
                                  context_instance=RequestContext(request))
      elif 'delete' in request.POST:
      #DELETE PROJECT WITH SPECIFIED TOKEN
        openid = request.user.username
        token = (request.POST.get('token')).strip()
        print " Ready to delete " ,token
        pd.deleteOCPCAProj(token)
         # pd.deleteTokenDescription(token)
        return redirect(tokens)
      elif 'downloadtoken' in request.POST:
      #DOWNLOAD TOKEN FILE
        token = (request.POST.get('token')).strip()
        print token
        response = HttpResponse(token,content_type='text/html')
        response['Content-Disposition'] = 'attachment; filename="ocpca.token"'
        return response
      elif 'update' in request.POST:
      #UPDATE PROJECT TOKEN -- FOLOWUP
        token = (request.POST.get('token')).strip()
        print token
        request.session["token"] = token
        return redirect(updateproject)
      return redirect(tokens)
    else:
      # GET datasets
      print "reached"
      openid = request.user.username
      if "project" in request.session:
        proj = request.session["project"]
        print proj
        #del request.session["project"]
        filteroption="project"
        projects = pd.getFilteredProjects ( openid ,filteroption,proj)
      else:
        proj = ""
        projects = pd.getFilteredProjects ( openid ,"","")
      return render_to_response('token.html', { 'tokens': projects, 'database': proj },context_instance=RequestContext(request))
    
  except OCPCAError, e:
    #return django.http.HttpResponseNotFound(e.value)
    datasets = pd.getDatasets()
    messages.error(request, e.value)
    return render_to_response('datasets.html', { 'dts': datasets },context_instance=RequestContext(request))





@login_required(login_url='/ocp/accounts/login/')
def createproject(request):

  if request.method == 'POST':
    if 'CreateProject' in request.POST:
      form = CreateProjectForm(request.POST)
   
      if form.is_valid():
                
        formset = ProjectFormSet(request.POST, instance=form.cleaned_data['dataset'])
        if formset.is_valid():
          formset.save()
  
        nocreateoption = request.POST.get('nocreate')
        if nocreateoption =="on":
          nocreate = 1
        else:
          nocreate = 0
        
        print "Creating a project with:"
        print  project, dataset, dataurl, exceptions, openid , resolution
        # Get database info                
        try:
          pd = ocpcaproj.OCPCAProjectsDB()
          pd.newOCPCAProj ( token, openid, host, project, datatype, dataset, dataurl, readonly, exceptions , nocreate, int(resolution) )
          #pd.insertTokenDescription ( token, description )
          return redirect(profile)          
        except OCPCAError, e:
          messages.error(request, e.value)
          return redirect(profile)          
      else:
        #Invalid Form
        context = {'form': form}
        print form.errors
        return render_to_response('createproject.html',context,context_instance=RequestContext(request))
    else:
      #default
      return redirect(profile)
  else:
    '''Show the Create projects form'''
    #randtoken = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(64))
    #form = CreateProjectForm(initial={'token': randtoken})
    #PYTODO - This should show both the create token form and create project form.
    # I am starting with create project which has a foreign key dependency on datasets.
    dataset_form = CreateDatasetForm()
    dataset = Dataset()
    formset = ProjectFormSet(instance=dataset)
    context = {'formset': formset}
    return render_to_response('createproject.html',context,context_instance=RequestContext(request))
      

@login_required(login_url='/ocp/accounts/login/')
def updateproject(request):
  
  #ocpcauser = request.user.get_profile
  #context = {'ocpcauser': ocpcauser}
  print "In update project view"
  if request.method == 'POST':
    if 'UpdateProject' in request.POST:
      form = UpdateProjectForm(request.POST)
      if form.is_valid():
#        import pdb;pdb.set_trace();
        curtoken = form.cleaned_data['currentToken']
        newtoken = form.cleaned_data['newToken']
        description = form.cleaned_data['description']
        pd = ocpcaproj.OCPCAProjectsDB()
        pd.updateProject(curtoken,newtoken)
        pd.updateTokenDescription ( newtoken ,description)
#pd.newOCPCAProj ( token, openid, host, project, datatype, dataset, dataurl, readonly, exceptions , nocreate )
        return redirect(profile)
       
      else:
        context = {'form': form}
        print form.errors
        return render_to_response('createproject.html',context,context_instance=RequestContext(request))
    else:
      return redirect(profile)
    
  else:
    print "Getting the update form"
    #token = (request.POST.get('token')).strip()
    if "token" in request.session:
      token = request.session["token"]
      del request.session["token"]
    else:
      token = ""
    randtoken = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(64))
    data = {'currentToken': token ,'newToken': randtoken}
    #data = {'newToken': randtoken}
    form = UpdateProjectForm(initial=data)
    context = {'form': form}
    return render_to_response('updateproject.html',context,context_instance=RequestContext(request))
      
@login_required(login_url='/ocp/accounts/login/')
def restore(request):
  if request.method == 'POST':
   
    if 'RestoreProject' in request.POST:
      form = CreateProjectForm(request.POST)
      if form.is_valid():
        token = form.cleaned_data['token']
        host = "localhost"
        project = form.cleaned_data['project']
        dataset = form.cleaned_data['dataset']
        datatype = form.cleaned_data['datatype']
        
        dataurl = "http://openconnecto.me/EM"
        readonly = form.cleaned_data['readonly']
        exceptions = form.cleaned_data['exceptions']
        nocreate = 0
        resolution = form.cleaned_data['resolution']
        openid = request.user.username
        print "Creating a project with:"
        #       print token, host, project, dataset, dataurl,readonly, exceptions, openid
        # Get database info
        pd = ocpcaproj.OCPCAProjectsDB()
        pd.newOCPCAProj ( token, openid, host, project, datatype, dataset, dataurl, readonly, exceptions , nocreate ,resolution)
        bkupfile = request.POST.get('backupfile')
        path = '/data/scratch/ocpbackup/'+ request.user.username + '/' + bkupfile
        if os.path.exists(path):
          print "File exists"
          
        proj= pd.loadProject(token)
        db=proj.getDBName()
        
        user ="brain"
        password ="88brain88"
        proc = subprocess.Popen(["mysql", "--user=%s" % user, "--password=%s" % password, db],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        proc.communicate(file(path).read())
        messages.success(request, 'Sucessfully restored database '+ db)
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
    path = '/data/scratch/ocpbackup/'+ request.user.username
    if os.path.exists(path):
      file_list =os.listdir(path)   
    else:
      file_list={}
    context = Context({'form': form, 'flist': file_list})
    return render_to_response('restoreproject.html',context,context_instance=RequestContext(request))


@login_required(login_url='/ocp/accounts/login/')
def get_datasets(request):
  try:
    pd = ocpcaproj.OCPCAProjectsDB()
   
    if request.method == 'POST':
      if 'delete' in request.POST:
        #delete specified dataset
        ds = (request.POST.get('dataset_name')).strip()
        ds_to_delete = Dataset.objects.get(dataset_name=ds)
        ds_to_delete.delete()
        all_datasets = Dataset.objects.all()
        return render_to_response('datasets.html', { 'dts': all_datasets },context_instance=RequestContext(request))
      elif 'update' in request.POST:
        ds = (request.POST.get('dataset_name')).strip()
        request.session["dataset_name"] = ds
        return redirect(updatedataset)
      #elif 'viewprojects' in request.POST:
       # pd = ocpcaproj.OCPCAProjectsDB()
       # openid = request.user.username
       # ds = (request.POST.get('dataset')).strip()
       # request.session["project"] = ds
       # filteroption= ""
       # filtervalue = ""
       # dbs = defaultdict(list)
       # proj = pd.getFilteredProjs(openid,filteroption,filtervalue,ds);
       # dbs[ds].append(proj)
       # return redirect(profile)
        #return render_to_response('profile.html', { 'projs': proj, 'databases':  dbs },context_instance=RequestContext(request))
      else:
        #Get all datasets
        all_datasets = Dataset.objects.all()
        return render_to_response('datasets.html', { 'dts': all_datasets },context_instance=RequestContext(request))
    else:
      # GET datasets
      all_datasets = Dataset.objects.all()
      return render_to_response('datasets.html', { 'dts': all_datasets },context_instance=RequestContext(request))
  except OCPCAError, e:
    all_datasets = Dataset.objects.all()  
    messages.error(request, e.value)
    return render_to_response('datasets.html', { 'dts': all_datasets },context_instance=RequestContext(request))    

@login_required(login_url='/ocp/accounts/login/')
def createdataset(request):

  if request.method == 'POST':
    if 'createdataset' in request.POST:
      form = CreateDatasetForm(request.POST)
      if form.is_valid():
        new_project= form.save()
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/datasets')
      #  return redirect(datasets)
      else:
        context = {'form': form}
        print form.errors
        return render_to_response('createdataset.html',context,context_instance=RequestContext(request))
    else:
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
#      
    else:
      ds = ""
    ds_to_update = Dataset.objects.select_for_update().filter(dataset_name=ds)
    data = {
      'dataset_name': ds_to_update[0].dataset_name,
      'ximagesize':ds_to_update[0].ximagesize,
      'yimagesize':ds_to_update[0].yimagesize,
      'startslice':ds_to_update[0].startslice,
      'endslice':ds_to_update[0].endslice,
      'zoomlevels':ds_to_update[0].zoomlevels,
      'zscale':ds_to_update[0].zscale,
      'dataset_description':ds_to_update[0].dataset_description,
            }
    form = CreateDatasetForm(initial=data)
    context = {'form': form}
    return render_to_response('updatedataset.html',context,context_instance=RequestContext(request))

