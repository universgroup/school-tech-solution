from django import forms
from django.forms import ModelForm
from .models import *


class FormMatiere(ModelForm):
    class Meta:
        model = Matiere
        fields = ('nom_matiere', 'coeff')
        labels = {
            'nom_matiere': 'Nom de la matière',
            'coeff': 'Coefficient'
        }
        widgets = {
            'nom_matiere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la matière',
                                                  'title': 'Saisissez le nom de la matière'}),
            'coeff': forms.NumberInput(attrs={'class': 'form-control', 'title': 'Saisissez le coefficient'})
        }

    def __init__(self, *args, **kwargs):
        super(FormMatiere, self).__init__(*args, **kwargs)
