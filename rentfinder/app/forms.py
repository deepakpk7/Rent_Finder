from django import forms
from .models import *

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = '__all__'
        widgets = {
            'available_from': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class VisitRequestForm(forms.ModelForm):
    class Meta:
        model = VisitRequest
        fields = ['user_name', 'phone_number', 'time_slot']