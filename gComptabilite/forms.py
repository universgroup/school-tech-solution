from django import forms
from django.forms import ModelForm
from .models import *


class FormCaisseScolarite(ModelForm):
    class Meta:
        model = Caisse
        fields = ('date_operation','anscolaire', 'type_operation', 'libelle_operation', 'categ_depense', 'montant_encaisse', 'observ')
        labels = {
            'date_operation': 'Date opération',
            'anscolaire': 'Année Scolaire',
            'type_operation': 'Type d\'opération',
            'libelle_operation': 'Désignation opération',
            'categ_depense': 'Catégorie recette',
            'montant_encaisse': 'Montant recette',
            'observ': 'Observation/Mémo'
        }
        widgets = {
            'date_operation': forms.DateInput(attrs={'class':'form-control','title':'Tapez la date exacte de l\'opération ou défilez dans le calendrier pour choisir la date exacte','type':'date'}),
            'anscolaire': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez une année scolaire'}),
            'type_operation': forms.Select(
                attrs={'class': 'form-control', 'title': 'Sélectionnez le type d\'opération de caisse'},
                choices=TYPE_OPERATION_CAISSE_CHOICES),
            'libelle_operation': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Libellé opération',
                                                       'title': 'Saisissez la désignation/libellé de votre opération',
                                                       'rows': '5', 'cols': '5', 'autocomplete': 'on'}),
            'categ_depense': forms.Select(
                attrs={'class': 'form-control', 'title': 'Sélectionnez la catégorie de recette'},
                choices=CATEGORIE_RECETTE_CHOICES),
            'montant_encaisse': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant opération',
                                                         'title': 'Saisissez le montant de l\'opération'}),
            'observ': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observation/Mémo',
                                             'title': 'Saisissez une observation/mémo pour votre opération'})
        }

    def __init__(self, *args, **kwargs):
        super(FormCaisseScolarite, self).__init__(*args, **kwargs)
        self.fields['anscolaire'].empty_label = 'Sélectionnez'
        self.fields['observ'].required = False


class FormDepense(ModelForm):
    class Meta:
        model = Caisse
        fields = (
            'date_operation','anscolaire', 'type_operation', 'libelle_operation', 'categ_depense', 'qte', 'pua', 'provient', 'destine',
            'observ', 'piece_jointe')
        labels = {
            'date_operation': 'Date opération',
            'anscolaire': 'Année scolaire',
            'type_operation': 'Type d\'opération',
            'libelle_operation': 'Désignation opération',
            'categ_depense': 'Catégorie dépense',
            'qte': 'Quantité',
            'pua': 'Prix unitaire',
            'provient': 'Provient de',
            'destine': 'Destiné à',
            'observ': 'Observation/Mémo',
            'piece_jointe': 'Pièce jointe'
        }
        widgets = {
            'date_operation' : forms.DateInput(attrs={'class':'form-control','title':'Tapez la date exacte de l\'opération ou défilez dans le calendrier pour choisir la date exacte','type':'date'}),
            'anscolaire': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez une année scolaire'}),
            'type_operation': forms.Select(
                attrs={'class': 'form-control', 'title': 'Sélectionnez le type d\'opération de caisse'},
                choices=TYPE_OPERATION_CAISSE_CHOICES),
            'libelle_operation': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Libellé opération',
                                                       'title': 'Saisissez la désignation/libellé de votre opération',
                                                       'rows': '5', 'cols': '5', 'autocomplete': 'on'}),
            'categ_depense': forms.Select(
                attrs={'class': 'form-control', 'title': 'Sélectionnez la catégorie de recette'},
                choices=CATEGORIE_DEPENSE_CHOICES),
            'qte': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Quantité depensée', 'title': 'Saisissez la quantité'}),
            'pua': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Prix unitaire', 'title': 'Saisissez le prix unitaire'}),
            'provient': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Provenance/Source',
                                               'title': 'Saisissez la source ou provenance du fonds'}),
            'destine': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination/Bénéficiaire',
                                              'title': 'Saisissez le bénéficiaire'}),
            'observ': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observation/Mémo',
                                             'title': 'Saisissez une observation/mémo pour votre opération'}),
            'piece_jointe': forms.FileInput(attrs={'class': 'form-control', 'title': 'Importez la pièce justificative'})
        }

    def __init__(self, *args, **kwargs):
        super(FormDepense, self).__init__(*args, **kwargs)
        self.fields['anscolaire'].empty_label = 'Sélectionnez'
        self.fields['piece_jointe'].required = False
        self.fields['observ'].required = False
