from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from models import Project
from models import Dataset
from models import Token


class CreateProjectForm(ModelForm):
#    ds_name = forms.ModelChoiceField(queryset = Dataset.objects.all())
   # ds_name1 = Dataset.objects.values_list('dataset_name', flat = True)
    class Meta:
        model = Project
        exclude = ['dataurl']
        exclude = ['dataset']

        def clean_project(self):
            if 'project' in self.cleaned_data:
                project = self.cleaned_data['project']
                return project
            raise forms.ValidationError('Please enter a valid project')
        
class CreateTokenForm(ModelForm):
#    ds_name = forms.ModelChoiceField(queryset = Dataset.objects.all())
   # ds_name1 = Dataset.objects.values_list('dataset_name', flat = True)
    class Meta:
        model = Token
        

        def clean_token(self):
            if 'token' in self.cleaned_data:
                token = self.cleaned_data['token']
                return token
            raise forms.ValidationError('Please enter a valid token')

class CreateDatasetForm(ModelForm):

    class Meta:
        model = Dataset
        

ProjectFormSet = inlineformset_factory(Dataset,Project,extra=1, form=CreateProjectForm)
TokenFormSet = inlineformset_factory(Project,Token,extra=1, form=CreateTokenForm)
             
class UpdateProjectForm(forms.Form):
    currentToken = forms.CharField(label=(u' Current Token'), widget = forms.TextInput(attrs={'readonly':'readonly'}))
    newToken = forms.CharField(label=(u' New Token'))
    description = forms.CharField(label=(u' Description'))
#    host = forms.CharField(label=(u'Host'))
#    project = forms.CharField(label=(u'Project'))
#    dataset = forms.CharField(label=(u'Dataset'))
#    dataurl = forms.CharField(initial='http://',label=(u'Data url'))
#    resolution = forms.IntegerField(label=(u'Resolution') ,error_messages=\
#{
#        "required": "This value cannot be empty.",
#        "invalid": "Please enter a valid Resolution",
#    })
#    readonly = forms.ChoiceField(choices=[(x, x) for x in range(0, 2)])
#    exceptions = forms.ChoiceField(choices=[(x, x) for x in range(0, 2)])
