from .models import *
from django import forms
from django.forms import ModelForm


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
            'nom_classe', 'frais_inscription', 'frais_reinscription', 'tranche1', 'idcycle')
        labels = {
            'nom_classe': 'Nom classe',
            'frais_inscription': 'Frais inscription',
            'frais_reinscription': 'Frais reinscription',
            'tranche1': 'Mensualité',
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
            'tranche1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Mensualité',
                                                 'title': 'Saisissez le montant de la mensualité'}),
            'idcycle': forms.Select(attrs={'class': 'form-control', 'selected': 'Selectionnez',
                                           'title': 'Sélectionnez le cycle associé à la classe'})
        }

    def __init__(self, *args,
                 **kwargs):
        super(FormClasse, self).__init__(*args, **kwargs)
        self.fields['idcycle'].empty_label = 'Sélectionnez'


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


class FormEleve(ModelForm):
    class Meta:
        model = Eleve
        fields = ('nom', 'prenom', 'sexe_eleve', 'pere', 'mere', 'tuteur', 'contact_parent', 'adresse',
                  'ecole_origine', 'photo_eleve', 'datenaissance', 'lieu_naissance', 'date_arrivee', 'pays_naissance')
        labels = {
            'nom': 'Nom Famille',
            'prenom': 'Prénoms',
            'sexe_eleve': 'Sexe',
            'pere': 'Prénoms du père',
            'mere': 'Nom & Prénoms mère',
            'tuteur': 'Nom & Prénoms tuteur',
            'contact_parent': 'Contact tuteur',
            'adresse': 'Adresse tuteur',
            'ecole_origine': 'Ecole d\'origine',
            'photo_eleve': 'Photo identité',
            'datenaissance': 'Date naissance',
            'lieu_naissance': 'Lieu naissance',
            'date_arrivee': 'Date d\'entrée',
            'pays_naissance': 'Pays naissance'
        }

        widgets = {
            'nom': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nom Famille', 'title': 'Saisissez le nom de famille'}),
            'prenom': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Prénoms', 'title': 'Saisissez le prénom'}),
            'sexe_eleve': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez le sexe_personnel'},
                                       choices=SEXE_ELEVE),
            'pere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénoms du père',
                                           'title': 'Saisissez le prénom du père'}),
            'mere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom & Prénoms mère',
                                           'title': 'Saisissez le nom et prénoms de la mère'}),
            'tuteur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom & Prénoms tuteur',
                                             'title': 'Saisissez le nom et prénoms du tuteur'}),
            'contact_parent': forms.TextInput(
                attrs={'class': 'validate', 'placeholder': 'Contact tuteur', 'type': 'tel',
                       'pattern': '^6(1|3|2|4|6|5)[0-9]{7}', 'min': '600000000',
                       'max': '699999999',
                       'title': 'Saisissez un numéro de téléphone guinéen'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse tuteur',
                                              'title': 'Saisissez l\'adresse du tuteur'}),
            'ecole_origine': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ecole d\'origine',
                                                    'title': 'Saisissez le nom de l\'école d\'origine'}),
            'photo_eleve': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpeg, .jpg, .JPEG, .JPG',
                                                  'title': 'Importez une photo pour l\'élève'}),
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


class FormInscription(ModelForm):
    class Meta:
        model = Inscription
        fields = ('annee_scolaire', 'idcycle', 'idclasse', 'regime_coran')  # 'mateleve'
        labels = {
            'annee_scolaire': 'Année scolaire',
            'idcycle': 'Cycle',
            'idclasse': 'Classe',
            'regime_coran': 'Regime coranique'
        }
        widgets = {
            'annee_scolaire': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez l\'année scolaire'}),
            'idcycle': forms.Select(
                attrs={'class': 'form-control', 'id': 'id_cycle', 'title': 'Sélectionnez le cycle'}),
            'idclasse': forms.Select(
                attrs={'class': 'form-control', 'id': 'id_classe', 'title': 'Sélectionnez la classe'}),
            'regime_coran': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez le regime coranique'},
                                         choices=REGIME_CORANIQUE_CHOICES)
        }

    def __init__(self, *args, **kwargs):
        super(FormInscription, self).__init__(*args, **kwargs)
        self.fields['idclasse'].queryset = Classe.objects.none()
        self.fields['annee_scolaire'].empty_label = 'Sélectionnez'
        self.fields['idcycle'].empty_label = 'Sélectionnez'

        if 'idcycle' in self.data:
            try:
                idc = int(self.data.get('idcycle'))
                self.fields['idclasse'].queryset = Classe.objects.filter(idcycle=idc)
            except(ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['idclasse'].queryset = self.instance.idcycle.idclasse_set.order_by('idcycle')


class FormAnneeScolaire(ModelForm):
    class Meta:
        model = AnneeScolaire
        fields = ['descript_annee']  # On utilise ici les listes quand la table n'a qu'un seul champ
        labels = {
            'descript_annee': 'Année Scolaire'
        }
        widgets = {
            'descript_annee': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2023-2024',
                                                     'title': 'Saisissez le descriptif de l\'année scolaire : 2023-2024 par exemple'})
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
            'bp_ecole': 'BP',
            'email_ecole': 'Email',
            'site_internet': 'Site web',
            'devise_ecole': 'Devise/Slogan',
            'dg': 'Nom et Prénoms DG',
            'coordo_primaire': 'Nom et Prénoms Coordinateur Primaire',
            'coordo_secondaire': 'Nom et Prénoms Coordinateur Secondaire',
            'comptable': 'Nom et Prénoms Comptable',
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
                                                 'pattern': '^6(1|2|3|4|5|6)[0-9]{7}', 'min': '600000000',
                                                 'max': '699999999',
                                                 'title': 'Saisissez un numéro de téléphone guinéen'}),
            'telephone2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact 2', 'type': 'tel',
                                                 'pattern': '^6(1|2|3|4|5|6)[0-9]{7}', 'min': '600000000',
                                                 'max': '699999999',
                                                 'title': 'Saisissez un numéro de téléphone guinéen'}),
            'agrement_ecole': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N°agrement',
                                                     'title': 'Saisissez le numéro de l\'agrement de votre école'}),
            'bp_ecole': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Boîte Postale (BP)',
                                               'title': 'Saisissez une boite postale'}),
            'email_ecole': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'contact@universtechgroup.com',
                       'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\\".[a-z]{2,4}$', 'title': 'Saisissez un email correct!'}),
            'site_internet': forms.URLInput(
                attrs={'class': 'form-control', 'placeholder': 'http://www.universtechgroup.com',
                       'pattern': "^(http(s)?:\\'/\\'/)+[\\'w\\'-\\'._~:\\'/?#[\\']@!\\'$&'\\'(\\')\\'*\\'+,;=.]+$",
                       'title': 'Saisissez un site web correct!'}),
            'devise_ecole': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Devise de l\'école',
                                                   'title': 'Saisissez la devise/slogan de l\'école'}),
            'dg': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom et Prénoms DG',
                                         'title': 'Saisissez le nom et prénoms du DG'}),
            'coordo_primaire': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nom et Prénoms Coordinateur Primaire',
                       'title': 'Saisissez le nom et prénoms du coordinateur du primaire'}),
            'coordo_secondaire': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nom et Prénoms Coordinateur Secondaire',
                       'title': 'Saisissez le nom et prénoms du coordinateur du secondaire'}),
            'comptable': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom et Prénoms Comptable',
                                                'title': 'Saisissez le nom et prénoms du/de la comptable'}),
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


class FormCaisseScolarite(ModelForm):
    class Meta:
        model = Caisse
        fields = ('anscolaire', 'type_operation', 'libelle_operation', 'categ_depense', 'montant_encaisse', 'observ')
        labels = {
            'anscolaire': 'Année Scolaire',
            'type_operation': 'Type d\'opération',
            'libelle_operation': 'Désignation',
            'categ_depense': 'Catégorie recette',
            'montant_encaisse': 'Montant recette',
            'observ': 'Observation/Mémo'
        }
        widgets = {
            'anscolaire': forms.Select(attrs={'class': 'form-control', 'title': 'Sélectionnez une année scolaire',
                                              'selected': 'Selectionnez'}),
            'type_operation': forms.Select(
                attrs={'class': 'form-control', 'title': 'Sélectionnez le type d\'opération de caisse'},
                choices=TYPE_OPERATION_CAISSE_CHOICES),
            'libelle_operation': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Libellé opération',
                                                       'title': 'Saisissez la désignation/libellé de votre opération'}),
            'categ_depense': forms.Select(
                attrs={'class': 'form-control', 'title': 'Sélectionnez la catégorie de recette'},
                choices=CATEGORIE_DEPENSE_CHOICES),
            'montant_encaisse': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Montant opération',
                                                         'title': 'Saisissez le montant de l\'opération'}),
            'observ': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observation/Mémo',
                                             'title': 'Saisissez une observation/mémo pour votre opération'})
        }

    def __init__(self, *args, **kwargs):
        super(FormCaisseScolarite, self).__init__(*args, **kwargs)
        self.fields['anscolaire'].empty_label = 'Sélectionnez'


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
