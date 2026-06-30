from django import forms
from django.forms import ModelForm
from .models import *
class FormCycle(ModelForm):
    class Meta:
        model = CycleScolaire
        fields = ['cycle']  # ('cycle',) Quand c'est un tuple
        labels = {
            'cycle': 'Cycle'
        }
        widget = {
            'cycle': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez le cycle'},
                                  choices=CYCLE_CHOICES)
        }

    def __init__(self, *args, **kwargs):
        super(FormCycle, self).__init__(*args, **kwargs)


class FormClasse(ModelForm):
    class Meta:
        model = Classe
        fields = (
            'nom_classe', 'frais_inscription', 'frais_reinscription', 'tranche1','tranche2','idcycle')
        labels = {
            'nom_classe': 'Nom classe',
            'frais_inscription': 'Frais inscription',
            'frais_reinscription': 'Frais reinscription',
            'tranche1': 'Première tranche',
            'tranche2':'Deuxième tranche',
            'idcycle': 'Cycle'
        }

        widgets = {
            'nom_classe': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la classe',
                                                 'title': 'Saisissez le nom de la classe'}),
            'frais_inscription': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Frais inscription',
                                                          'title': 'Saisissez le frais d\'inscription'}),
            'frais_reinscription': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Frais reinscription',
                       'title': 'Saisissez le frais de réinscription'}),
            'tranche1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tranche 1',
                                                 'title': 'Saisissez le montant de la première tranche'}),
            'tranche2': forms.NumberInput(attrs={'class':'form-control','placeholder':'Tranche 2','title':'Saisissez le montant de la deuxième tranche'}),
            'idcycle': forms.Select(attrs={'class': 'form-control', 'selected': 'Selectionnez',
                                           'title': 'Sélectionnez le cycle associé à la classe'})
        }

    def __init__(self, *args,
                 **kwargs):
        super(FormClasse, self).__init__(*args, **kwargs)
        self.fields['idcycle'].empty_label = 'Sélectionnez'

class FormAnneeScolaire(ModelForm):
    class Meta:
        model = AnneeScolaire
        fields = ['descript_annee']  # On utilise ici les listes quand la table n'a qu'un seul champ
        labels = {
            'descript_annee': 'Année Scolaire'
        }
        widgets = {
            'descript_annee': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2024-2025',
                                                     'title': 'Saisissez le descriptif de l\'année scolaire : 2024-2025 par exemple'})
        }

    def __init__(self, *args, **kwargs):
        super(FormAnneeScolaire, self).__init__(*args, **kwargs)


class FormEcole(ModelForm):
    class Meta:
        model = Ecole
        fields = (
            'nom_ecole', 'ville_ecole', 'prefect_commune', 'dsee', 'telephone1', 'telephone2', 'agrement_ecole',
            'bp_ecole',
            'email_ecole', 'site_internet', 'devise_ecole', 'dg', 'coordo_primaire', 'coordo_secondaire', 'comptable',
            'logo_ecole', 'signa_dg', 'signa_de')  # '__all__'
        labels = {
            'nom_ecole': 'Nom école/Raison sociale',
            'ville_ecole': 'IRE',
            'prefect_commune': 'DCE/DPE',
            'dsee': 'DSEE',
            'telephone1': 'Contact 1',
            'telephone2': 'Contact 2',
            'agrement_ecole': 'N°agrement',
            'bp_ecole': 'Boite Postale(BP)',
            'email_ecole': 'Email/Adresse electronique',
            'site_internet': 'Site web',
            'devise_ecole': 'Devise/Slogan',
            'dg': 'Directeur(trice) Général(e)',
            'coordo_primaire': 'Coordinateur Primaire',
            'coordo_secondaire': 'Coordinateur Secondaire',
            'comptable': 'Comptable',
            'logo_ecole': 'Logo école',
            'signa_dg': 'Signature du DG',
            'signa_de': 'Signature du DE'

        }
        widgets = {
            'nom_ecole': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nom/Raison sociale de l\'école',
                       'title': 'Saisissez la raison sociale de votre école'}),
            'ville_ecole': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'IRE', 'title': 'Saisissez le nom de l\'IRE'}),
            'prefect_commune': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'DCE/DPE', 'title': 'Saisissez le nom de la DCE/DPE'}),
            'dsee': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'DSEE', 'title': 'Saisissez le nom de la DSEE'}),
            'telephone1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact 1', 'type': 'tel',
                                                 'pattern': "(\\+224)?[36][0-9]{8}",
                                                 'title': 'Saisissez un numéro de téléphone guinéen'}),
            'telephone2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact 2', 'type': 'tel',
                                                 'pattern': "(\\+224)?[36][0-9]{8}",
                                                 'title': 'Saisissez un numéro de téléphone guinéen'}),
            'agrement_ecole': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N°agrement',
                                                     'title': 'Saisissez le numéro de l\'agrement de votre école'}),
            'bp_ecole': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Boîte Postale (BP)',
                                               'title': 'Saisissez une boite postale'}),
            'email_ecole': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'Ex: contact@universtechgroup.com',
                       'pattern': "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\'.[a-zA-Z]{2,}", 'title': 'Saisissez un email correct!'}),
            'site_internet': forms.URLInput(
                attrs={'class': 'form-control', 'placeholder': 'Ex: https://www.universtechgroup.com',
                       'pattern': "https?://[a-zA-Z0-9.-]+\\'.[a-zA-Z]{2,}.*",
                       'title': 'Saisissez un site web correct!'}),
            'devise_ecole': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Devise de l\'école',
                                                   'title': 'Saisissez la devise/slogan de l\'école'}),
            'dg': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénoms et Nom DG',
                                         'title': 'Saisissez le prénoms et nom du/de la Directeur(trice) Général(e)'}),
            'coordo_primaire': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Prénoms et Nom du Coordinateur Primaire',
                       'title': 'Saisissez le prénoms et nom du coordinateur du primaire'}),
            'coordo_secondaire': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Prénoms et Nom du Coordinateur Secondaire',
                       'title': 'Saisissez le prénoms et nom du coordinateur du secondaire'}),
            'comptable': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénoms et Nom Comptable',
                                                'title': 'Saisissez le prénoms et nom du/de la comptable'}),
            'logo_ecole': forms.FileInput(
                attrs={'class': 'form-control', 'title': 'Importez le logo de l\'école',
                       'accept': 'image/jpeg, image/png'}),
            'signa_dg': forms.FileInput(
                attrs={'class': 'form-control', 'title': 'Importez la signature du DG',
                       'accept': 'image/jpeg, image/png'}),
            'signa_de': forms.FileInput(
                attrs={'class': 'form-control', 'title': 'Importez la signature du DE',
                       'accept': 'image/jpeg, image/png'})  # 'accept': 'image/jpeg, image/png, image/*'

        }

    def __init__(self, *args, **kwargs):
        super(FormEcole, self).__init__(*args, **kwargs)
        self.fields['telephone2'].required = False
        self.fields['bp_ecole'].required = False
        self.fields['logo_ecole'].required = False
        self.fields['signa_dg'].required = False
        self.fields['signa_de'].required = False
        self.fields['email_ecole'].required=False
        self.fields['site_internet'].required=False
        self.fields['coordo_primaire'].required=False
        
        
