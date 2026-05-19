from django import forms
from django.forms import ModelForm
from .models import *

class FormPersonnel(ModelForm):
    class Meta:
        model = Personnel
        # fields =__all__
        fields = ('nom_personnel', 'prenom_personnel', 'civilite', 'date_naissance', 'niveau_etude', 'type_personnel',
                  'adresse_personnel', 'contact_personnel', 'fonction_personnel', 'email_personnel', 'sexe_personnel',
                  'salbase',
                  'annee_experience', 'contrat_type', 'diplome', 'date_embauche')
        labels = {
            'nom_personnel': 'Nom Famille',
            'prenom_personnel': 'Prénom(s) Personnel',
            'civilite': 'Civilité',
            'date_naissance': 'Date naissance',
            'niveau_etude': 'Niveau étude',
            'type_personnel': 'Type personnel',
            'adresse_personnel': 'Adresse',
            'contact_personnel': 'Contact',
            'fonction_personnel': 'Fonction',
            'email_personnel': 'Email',
            'sexe_personnel': 'Genre',
            'salbase': 'Salaire de base',
            'annee_experience': 'Année d\'expérience',
            'contrat_type': 'Type contrat',
            'diplome': 'Diplôme',
            'date_embauche': 'Date d\'embauche'
        }
        widgets = {
            'nom_personnel': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nom Famille', 'title': 'Saisissez le nom de famille'}),
            'prenom_personnel': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Prénom(s) du Personnel',
                       'title': 'Saisissez le prénoms'}),
            'civilite': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez la civilité'},
                                     choices=CIVILITE_CHOICES),
            'date_naissance': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date', 'title': 'Sélectionnez/tapez la date de naissance'}),
            'niveau_etude': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Niveau d\'étude du personnel',
                       'title': 'Saisissez le niveau d\'étude du personnel'}),
            'type_personnel': forms.Select(attrs={'class': 'form-control',
                                                  'title': 'Sélectionnez la catégorie/type auquel appartient le personnel'},
                                           choices=TYPE_PERSONNEL),
            'adresse_personnel': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Adresse du Personnel',
                       'title': 'Saisissez l\'adresse du personnel'}),
            'contact_personnel': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'N°Téléphone du Personnel', 'type': 'tel',
                       'pattern': '^6(1|2|5|6|3|)[0-9]{7}', 'min': '600000000', 'max': '699999999',
                       'title': 'Saisissez un numéro de téléphone guinéen'}),
            'fonction_personnel': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Fonction du Personnel',
                       'title': 'Saisissez la fonction du personnel'}),
            'email_personnel': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'contact@universtechgroup.com',
                       'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\\".[a-z]{2,4}$', 'title': 'Saisissez un email correct!'}),
            'sexe_personnel': forms.Select(
                attrs={'class': 'form-control', 'title': 'Sélectionnez le genre du personnel'}, choices=SEXE_PERSONNEL),
            'salbase': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Salaire de Base',
                       'title': 'Saisissez le salaire de base'}),
            'annee_experience': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nombre d\'année d\'expérience',
                       'title': 'Saisissez le nombre d\'année d\'expérience'}),
            'contrat_type': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez le type de contrat'},
                                         choices=CONTRAT_CHOICES),
            'diplome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Diplôme d\'étude',
                                              'title': 'Saisissez le diplôme obtenu par le personnel'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date',
                                                    'title': 'Sélectionnez/tapez la date d\'embauche du personnel'})

        }

    def __init__(self, *args, **kwargs):
        super(FormPersonnel, self).__init__(*args, **kwargs)


class FormSalaire(ModelForm):
    class Meta:
        model = Salaire
        fields = (
            'anneescolaire', 'mois_paie', 'idpersonnel', 'nbre_heure', 'taux_horaire', 'primes', 'nb_hsupp',
            'mont_hsupp', 'detail_paiement')
        labels = {
            'anneescolaire': 'Année scolaire',
            'mois_paie': 'Mois paiement',
            'idpersonnel': 'Employé',
            'nbre_heure': 'Nombre d\'heures enseignées',
            'taux_horaire': 'Taux horaire',
            'primes': 'Montant des primes',
            'nb_hsupp': 'Nombre d\'heures supplementaires',
            'mont_hsupp': 'Montant des heures supplementaires',
            'detail_paiement': 'Detail Paiement'
        }
        widgets = {
            'anneescolaire': forms.Select(
                attrs={'class': 'form-control', 'title': 'Sélectionnez l\'année scolaire courante'}),
            'mois_paie': forms.Select(
                attrs={'class': 'form-control', 'placeholder': 'Mois Paiement', 'title': 'Sélectionnez le mois payé'},
                choices=MOIS_CHOICES),
            'idpersonnel': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez l\'employé à payer'}),
            'nbre_heure': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Nombre d\'heures enseignées',
                       'title': 'Saisissez le nombre d\'heures enseignées'}),
            'taux_horaire': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Taux horaire', 'title': 'Saisissez le taux horaire'}),
            'primes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant des Primes',
                                               'title': 'Saisissez le montant des primes perçues'}),
            'nb_hsupp': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Nombre d\'heures supplementaires',
                       'title': 'Saisissez le nombre d\'heures supp'}),
            'mont_hsupp': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Montant des heures supplementaires',
                       'title': 'Saisissez le montant des heures supplementaires'}),
            'detail_paiement': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Detail du Paiement', 'cols': '10', 'rows': '5',
                       'title': 'Saisissez un intitulé pour le paiement'})
        }

    def __init__(self, *args, **kwargs):
        super(FormSalaire, self).__init__(*args, **kwargs)
        self.fields['detail_paiement'].required = False
        self.fields['idpersonnel'].empty_label = 'Sélectionnez'
        self.fields['anneescolaire'].empty_label = 'Sélectionnez'


class FormAvanceSalaire(ModelForm):
    class Meta:
        model = AvanceSalaire
        fields = ('anscolaire', 'mois_avance', 'idpersonnel', 'intitule', 'montant_avance')
        labels = {
            'anscolaire': 'Année scolaire',
            'mois_avance': 'Mois',
            'idpersonnel': 'Employé',
            'intitule': 'Description',
            'montant_avance': 'Montant avancé',
        }
        widgets = {
            'anscolaire': forms.Select(
                attrs={'class': 'form-control', 'title': 'Sélectionnez l\'année scolaire courante'}),
            'mois_avance': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez le mois de l\'avance'},
                                        choices=MOIS_CHOICES),
            'idpersonnel': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez un employé'}),
            'intitule': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Description de l\'opération', 'cols': '10',
                       'rows': '5', 'title': 'Saisissez une description pour l\'opération'}),
            'montant_avance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant avancé',
                                                       'title': 'Saisissez le montant de l\'avance'}),
        }

    def __init__(self, *args, **kwargs):
        super(FormAvanceSalaire, self).__init__(*args, **kwargs)
        self.fields['intitule'].required = False
        self.fields['anscolaire'].empty_label = 'Sélectionnez'
        self.fields['idpersonnel'].empty_label = 'Sélectionnez'
