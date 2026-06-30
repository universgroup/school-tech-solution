from django import forms
from django.forms import ModelForm
from .models import *


class FormEleve(ModelForm):
    class Meta:
        model = Eleve
        fields = ('nom', 'prenom', 'sexe_eleve', 'pere', 'mere', 'tuteur', 'contact_parent','email_parent', 'adresse',
                  'ecole_origine', 'photo_eleve', 'datenaissance', 'lieu_naissance', 'date_arrivee', 'pays_naissance')
        labels = {
            'nom': 'Nom Famille',
            'prenom': 'Prénoms',
            'sexe_eleve': 'Sexe',
            'pere': 'Prénoms du père',
            'mere': 'Prénoms & Nom de la mère',
            'tuteur': 'Prénoms & Nom du tuteur',
            'contact_parent': 'Contact du tuteur',
            'email_parent':'Email du tuteur/parent',
            'adresse': 'Adresse du tuteur',
            'ecole_origine': 'Ecole d\'origine',
            'photo_eleve': 'Photo identité',
            'datenaissance': 'Date naissance',
            'lieu_naissance': 'Lieu naissance',
            'date_arrivee': 'Date d\'entrée',
            'pays_naissance': 'Pays naissance'
        }

        widgets = {
            'nom': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nom Famille', 'title': 'Saisissez le nom de famille',
                       'id': 'idnom'}), # Cet idnom est utilisé dans le template par JQuery pour transformer le nom de famille saisi en majuscule
            'prenom': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Prénoms', 'title': 'Saisissez le prénom',
                       'id': 'idprenom'}),
            'sexe_eleve': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez le sexe_personnel'},
                                       choices=SEXE_ELEVE_CHOICES),
            'pere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénoms du père',
                                           'title': 'Saisissez le prénom du père'}),
            'mere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom & Prénoms mère',
                                           'title': 'Saisissez le prénoms et nom de la mère'}),
            'tuteur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom & Prénoms tuteur',
                                             'title': 'Saisissez le prénoms et nom du tuteur'}),
            'contact_parent': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Contact du tuteur', 'type': 'tel',
                       'pattern': '(\\+224)?[36][0-9]{8}','title': 'Saisissez un numéro de téléphone guinéen'}),
            'email_parent': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex: contact@universtechgroup.com',
                       'pattern': "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\'.[a-zA-Z]{2,}", 'title': 'Saisissez un email correct!'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse tuteur',
                                              'title': 'Saisissez l\'adresse du tuteur'}),
            'ecole_origine': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ecole d\'origine',
                                                    'title': 'Saisissez le nom de l\'école d\'origine'}),
            'photo_eleve': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg, image/png',
                                                  'title': 'Importez la photo de l\'élève si disponible'}),
            'datenaissance': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date', 'title': 'Sélectionnez la date de naissance'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu naissance',
                                                     'title': 'Saisissez le lieu de naissance'}),
            'date_arrivee': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date', 'title': 'Saisissez la date d\'entrée'}),
            'pays_naissance': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pays naissance',
                                                     'title': 'Saisissez le pays de naissance'})
        }

    def __init__(self, *args, **kwargs):
        super(FormEleve, self).__init__(*args, **kwargs)
        self.fields[
            'photo_eleve'].required = False  # Permet de rendre non obligatoire la selection de la photo d'un élève
        self.fields['email_parent'].required = True


class FormInscription(ModelForm):
    class Meta:
        model = Inscription
        fields = ('annee_scolaire', 'idcycle', 'idclasse')  # 'mateleve
        labels = {
            'annee_scolaire': 'Année scolaire',
            'idcycle': 'Cycle',
            'idclasse': 'Classe'
        }
        widgets = {
            'annee_scolaire': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez l\'année scolaire'}),
            'idcycle': forms.Select(
                attrs={'class': 'form-control', 'id': 'id_cycle', 'title': 'Sélectionnez le cycle'}),
            'idclasse': forms.Select(
                attrs={'class': 'form-control', 'id': 'id_classe', 'title': 'Sélectionnez la classe'})            
        }

    def __init__(self, *args, **kwargs):
        super(FormInscription, self).__init__(*args, **kwargs)
        self.fields['idclasse'].queryset = Classe.objects.none()
        self.fields['annee_scolaire'].empty_label = 'Sélectionnez'
        self.fields['idcycle'].empty_label = 'Sélectionnez'
        self.fields['idclasse'].empty_label = 'Sélectionnez'

        if 'idcycle' in self.data:
            try:
                idc = int(self.data.get('idcycle'))
                self.fields['idclasse'].queryset = Classe.objects.filter(idcycle=idc)
            except(ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['idclasse'].queryset = self.instance.idcycle.idclasse_set.order_by('idcycle')
