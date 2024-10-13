from django_select2.forms import Select2Widget
from django.contrib import admin
from .models import HomeCareCategory, HomeCareService
from django import forms

class HomeCareServiceAdminForm(forms.ModelForm):
    class Meta:
        model = HomeCareService
        fields = '__all__'
        widgets = {
            'category': Select2Widget
        }
