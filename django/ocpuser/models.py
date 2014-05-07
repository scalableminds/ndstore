from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

# This model represent and creates an ocp dataset( database)
class Dataset ( models.Model):
    dataset_name  =  models. CharField(max_length=200, unique=True,verbose_name="Name of the Image dataset")    
    ximagesize =  models.IntegerField()
    yimagesize =  models.IntegerField()
    startslice = models.IntegerField()
    endslice = models.IntegerField()
    zoomlevels = models.IntegerField()
    zscale = models.FloatField()
    dataset_description  =  models. CharField(max_length=4096)
    
    class Meta:
        """ Meta """
        # Required to override the default table name
        db_table = u"datasets"
        managed = True
        permissions = (
            ("can_administer", "Can administer projects"),
            ("can_delete", "Can delete projects"),
            ("can_browse", "Can browse projects")
        )

    def __unicode__(self):
        return self.dataset_name


# This model represent and creates an ocp project( database)
# It has a foreign key dependency on the datasets class
class Project ( models.Model):
    project_name  =  models. CharField(max_length=200, primary_key=True)
    project_description  =  models. CharField(max_length=4096, blank=True)
    dataset  =  models.ForeignKey(Dataset)

    DATATYPE_CHOICES = (
        (1, 'IMAGES'),
        (2, 'ANNOTATIONS'),
        (3, 'CHANNEL_16bit'),
        (4, 'CHANNEL_8bit'),
        (5, 'PROBMAP_32bit'),
        (6, 'BITMASK'),
        (7, 'ANNOTATIONS_64bit'),
        )
    datatype = models.IntegerField(choices=DATATYPE_CHOICES, default=1)
    dataurl  =  "http://openconnecto.me/ocp"
    resolution = models.IntegerField(default=0)
    EXCEPTION_CHOICES = (
        (1, 'Yes'),
        (0, 'No'),
        )
    exceptions =  models.IntegerField(choices=EXCEPTION_CHOICES, default=2)
    HOST_CHOICES = (
        ('localhost', 'localhost'),
        ('braingraph1.cs.jhu.edu', 'openconnecto.me'),
        ('braingraph1dev.cs.jhu.edu', 'braingraph1dev'),
        ('braingraph2.cs.jhu.edu', 'braingraph2'),
        ('dsp029.pha.jhu.edu', 'Datascope 029'),
        ('dsp061.pha.jhu.edu', 'Datascope 061'),
        ('dsp062.pha.jhu.edu', 'Datascope 062'),
        ('dsp063.pha.jhu.edu', 'Datascope 063'),
        )
    host =  models.CharField(max_length=200, choices=HOST_CHOICES, default='localhost')
#    NOCREATE_CHOICES = (
 #       (0, 'No'),
 #       (1, 'Yes'),
 #       )
 #   nocreate =  models.IntegerField(choices=NOCREATE_CHOICES, default=0)

    class Meta:
        """ Meta """
        # Required to override the default table name
        db_table = u"projects"
    def __unicode__(self):
        return self.project


class Token ( models.Model):
    token_name  =  models. CharField(max_length=200, primary_key=True)
    token_description  =  models. CharField(max_length=4096,blank=True)
    project  = models.ForeignKey(Project)
    READONLY_CHOICES = (
        (1, 'Yes'),
        (0, 'No'),
        )
    readonly =  models.IntegerField(choices=READONLY_CHOICES, default=2)
    PUBLIC_CHOICES = (
        (1, 'Yes'),
        (0, 'No'),
        )
    public =  models.IntegerField(choices=PUBLIC_CHOICES, default=2)
    
    
    class Meta:
        """ Meta """
         # Required to override the default table name
        db_table = u"tokens"
    def __unicode__(self):
        return self.token
