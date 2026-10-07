from django import forms
from django.forms import ModelForm
from .models import *
from django.core.exceptions import ValidationError

import re

EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

class FormPersonnel(ModelForm):
    class Meta:
        model = Personnel
        # fields =__all__
        fields = ('nom_personnel', 'prenom_personnel', 'civilite', 'date_naissance','lieu_naissance', 'niveau_etude', 'type_personnel','adresse_personnel', 'contact_personnel', 'fonction_personnel', 'email_personnel', 'sexe_personnel','salbase','annee_experience', 'contrat_type', 'diplome', 'date_embauche','etat_matrimonial','annee_scolaire','photo_employe')
        labels = {
            'nom_personnel': 'Nom Famille',
            'prenom_personnel': 'Prénom(s)',
            'civilite': 'Civilité',
            'date_naissance': 'Date naissance',
            'lieu_naissance': 'Lieu naissance',
            'niveau_etude': 'Niveau étude',
            'type_personnel': 'Catégorie personnel',
            'adresse_personnel': 'Adresse/Résidence',
            'contact_personnel': 'N°Téléphone',
            'fonction_personnel': 'Fonction/Poste occupé',
            'email_personnel': 'Email',
            'sexe_personnel': 'Genre(Sexe)',
            'salbase': 'Salaire de base',
            'annee_experience': 'Nombre d\'année d\'expérience',
            'contrat_type': 'Type de contrat',
            'diplome': 'Diplôme le plus elevé',
            'date_embauche': 'Date d\'embauche',
            'etat_matrimonial': 'Situation matrimoniale',
            'annee_scolaire': 'Année scolaire',
            'photo_employe': 'Photo identité',
        }
        widgets = {
            'nom_personnel': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nom Famille', 'title': 'Saisissez le nom de famille','id':'id_nom_emp'}),
            'prenom_personnel': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Prénom(s)',
                       'title': 'Saisissez les prénoms du personnel','id':'id_prenom_emp'}),
            'civilite': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez la civilité'},
                                     choices=CIVILITE_CHOICES),
            'date_naissance': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date', 'title': 'Sélectionnez/tapez la date de naissance'}),
            'lieu_naissance' : forms.TextInput(attrs={'class':'form-control','placeholder':'Lieu naissance', 'title':'Saisissez le lieu de naissance du personnel'}),
            'niveau_etude': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Niveau d\'étude du personnel',
                       'title': 'Saisissez le niveau d\'étude du personnel (Primaire, Secondaire, Universitaire)'}),
            'type_personnel': forms.Select(attrs={'class': 'form-control',
                                                  'title': 'Sélectionnez la catégorie/type auquel appartient le personnel'},
                                           choices=TYPE_PERSONNEL),
            'adresse_personnel': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Adresse du Personnel',
                       'title': 'Saisissez l\'adresse du personnel'}),
            'contact_personnel': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'N°Téléphone', 'type': 'tel',
                       'pattern': r"^(\+?[0-9]{1,3}[\s\-]?)?[0-9\s\-\(\)]{7,15}$",
                       'title': 'Saisissez un numéro de téléphone valide avec ou sans code du pays'}),
            'fonction_personnel': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Fonction/Poste du Personnel',
                       'title': 'Saisissez la fonction/poste du personnel'}),
            'email_personnel': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'Ex : contact@universtechgroup.com',
                       'title': 'Saisissez un email correct!'}),
            'sexe_personnel': forms.Select(
                attrs={'class': 'form-control', 'title': 'Sélectionnez le genre du personnel'}, choices=SEXE_PERSONNEL),
            'salbase': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Salaire de Base',
                       'title': 'Saisissez le salaire de base'}),
            'annee_experience': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nombre d\'année d\'expérience',
                       'title': 'Saisissez le nombre d\'année d\'expérience'}),
            'contrat_type': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez le type de contrat'}, choices=CONTRAT_CHOICES),
            'diplome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Diplôme d\'étude',
                                              'title': 'Saisissez le diplôme obtenu par le personnel'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date',
                                                    'title': 'Sélectionnez/tapez la date d\'embauche du personnel'}),
            'etat_matrimonial' : forms.Select(attrs={'class':'form-control', 'title':'Sélectionnez le statut matrimonial'}, choices=STATUT_MATRIMONIAL),
            'annee_scolaire' : forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez l\'année scolaire relative à son engagement'}),
            'photo_employe': forms.FileInput(attrs={'id':'idphotoemp', 'class': 'd-none', 'title': 'Importez la photo de l\'employé', 'accept': 'image/*', 'onchange' : 'previewPhotoEmploye(this)'}),


        }

    def __init__(self, *args, **kwargs):
        super(FormPersonnel, self).__init__(*args, **kwargs)
        self.fields['photo_employe'].required = False
        self.fields['annee_scolaire'].empty_label = 'Sélectionnez'

        def clean_email_personnel(self):
            emailpersonnel = self.cleaned_data.get('email_personnel')
            if emailpersonnel and not re.match(EMAIL_PATTERN, emailpersonnel):
                raise ValidationError("Format d'email invalide pour le personnel.")
            return emailpersonnel


class FormSalaire(ModelForm):
    class Meta:
        model = Salaire
        fields = ('anneescolaire','date_paiement', 'mois_paie', 'idpersonnel', 'nbre_heure', 'taux_horaire', 'avance_paie', 'primes', 'salbrut', 'cotis_sociale', 'salnet', 'nb_hsupp','mont_hsupp', 'detail_paiement')
        labels = {
            'anneescolaire': 'Année scolaire',
            'date_paiement' : 'Date paiement',
            'mois_paie': 'Mois paiement',
            'idpersonnel': 'Employé',
            'nbre_heure': 'Nombre d\'heures enseignées',
            'taux_horaire': 'Taux horaire',
            'avance_paie': 'Montant des avances',
            'primes': 'Montant des primes',
            'salbrut': 'Salaire brut',
            'cotis_sociale': 'Montant cotisation sociale',
            'salnet': 'Salaire net',
            'nb_hsupp': 'Nombre d\'heures supplementaires',
            'mont_hsupp': 'Montant des heures supplementaires',
            'detail_paiement': 'Libellé du paiement',
        }
        widgets = {
            'anneescolaire': forms.Select(
                attrs={'class': 'form-control', 'title': 'Sélectionnez l\'année scolaire courante','id':'id_anscol'}),

            'date_paiement' : forms.DateInput(attrs={'type':'date', 'class':'form-control', 'title': 'Saisissez la date de paiement du salaire'}),

            'mois_paie': forms.Select(
                attrs={'class': 'form-control', 'title': 'Sélectionnez le mois payé','id':'id_mois_paie'},
                choices=MOIS_CHOICES),

            'idpersonnel': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez l\'employé à payer', 'id':'idemploye'}),

            'nbre_heure': forms.NumberInput(attrs={'class': 'form-control', 'title': 'Saisissez le nombre d\'heures enseignées', 'value': '0', 'id': 'id_nbr_heure'}),

            'taux_horaire': forms.NumberInput(attrs={'class': 'form-control', 'title': 'Saisissez le taux horaire', 'value': '0', 'id': 'id_taux_horaire'}),

            'avance_paie': forms.TextInput(attrs={'class': 'form-control', 'readonly':True, 'title': 'Affiche le montant des avances perçues par l\'employé', 'placeholder': 'Montant des avances', 'id': 'id_avance_paie'}),

            'primes': forms.NumberInput(attrs={'class': 'form-control','title': 'Saisissez le montant des primes perçues', 'value': '0', 'id': 'id_prime'}),

            'salbrut': forms.TextInput(attrs={'class': 'form-control', 'readonly': True, 'title': 'Affiche le salaire brut obtenu après calcul', 'placeholder': 'Salaire brut', 'id': 'id_salb'}),

            'cotis_sociale' : forms.NumberInput(attrs={'class': 'form-control', 'title': 'Saisissez le montant de la cotisation sociale si existe', 'value': '0', 'id': 'id_coti_social'}),

            'salnet': forms.TextInput(attrs={'class': 'form-control', 'title': 'Affiche le salaire net obtenu après calcul', 'readonly': True, 'placeholder': 'Salaire net', 'id': 'id_salnet'}),

            'nb_hsupp': forms.NumberInput(
                attrs={'class': 'form-control','title': 'Saisissez le nombre d\'heures supp', 'value': '0'}),

            'mont_hsupp': forms.NumberInput(
                attrs={'class': 'form-control', 'title': 'Saisissez le montant des heures supplementaires', 'value': '0', 'id': 'id_mnt_hsupp'}),

            'detail_paiement': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Detail du Paiement', 'cols': '5', 'rows': '5','title': 'Affiche le libellé du paiement', 'readonly': True, 'id': 'id_detail_paie'}),
        }

    def __init__(self, *args, **kwargs):
        super(FormSalaire, self).__init__(*args, **kwargs)
        self.fields['detail_paiement'].required = False
        self.fields['avance_paie'].required = False
        self.fields['primes'].required = False
        self.fields['salbrut'].required = False
        self.fields['cotis_sociale'].required = False
        self.fields['salnet'].required = False
        self.fields['nb_hsupp'].required = False
        self.fields['mont_hsupp'].required = False
        self.fields['nbre_heure'].required = False
        self.fields['taux_horaire'].required = False


        self.fields['idpersonnel'].empty_label = 'Sélectionnez'
        self.fields['anneescolaire'].empty_label = 'Sélectionnez'


class FormAvanceSalaire(ModelForm):
    class Meta:
        model = AvanceSalaire
        fields = ('anscolaire', 'mois_avance', 'idpersonnel', 'intitule', 'montant_avance', 'date_avance')
        labels = {
            'anscolaire': 'Année scolaire',
            'mois_avance': 'Mois',
            'idpersonnel': 'Employé',
            'intitule': 'Libellé du bon/avance de paiement',
            'montant_avance': 'Montant avancé',
            'date_avance': 'Date paiement',
        }
        widgets = {
            'anscolaire': forms.Select(
                attrs={'class': 'form-control', 'title': 'Sélectionnez l\'année scolaire courante'}),

            'mois_avance': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez le mois de l\'avance'},choices=MOIS_CHOICES),

            'idpersonnel': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez un employé', 'id': 'id_employe'}),

            'intitule': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Description du bon de paiement', 'cols': '5','rows': '5', 'title': 'Affiche le libellé du paiement', 'readonly': True}),

            'montant_avance': forms.NumberInput(attrs={'class': 'form-control', 'title': 'Saisissez le montant de l\'avance ou du bon de paiement', 'value': '0'}),

            'date_avance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'title': 'Saisissez la date de paiement de l\'avance'}),
        }

    def __init__(self, *args, **kwargs):
        super(FormAvanceSalaire, self).__init__(*args, **kwargs)
        self.fields['intitule'].required = False
        self.fields['anscolaire'].empty_label = 'Sélectionnez'
        self.fields['idpersonnel'].empty_label = 'Sélectionnez'
