from django.db import models

CYCLE_CHOICES = [
    ('Selectionnez', 'Sélectionnez'),
    ('Maternelle', 'Maternelle'),
    ('Primaire', 'Primaire'),
    ('Collège', 'Collège'),
    ('Lycée SM', 'Lycée SM'),
    ('Lycée SS', 'Lycée SS'),
    ('Lycée SE', 'Lycée SE')
]

CIVILITE_CHOICES = [
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Monsieur', 'Monsieur'),  # 1
    ('Madame', 'Madame'),  # 2
    ('Madémoiselle', 'Madémoisselle')  # 3
]

TYPE_PERSONNEL = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Vacataire', 'Vacataire'),  # 1
    ('Permanent', 'Permanent')  # 2
)

SEXE_PERSONNEL = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Homme', 'Homme'),  # 1
    ('Femme', 'Femme')  # 2
)

SEXE_ELEVE = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Masculin', 'Masculin'),  # 1
    ('Feminin', 'Feminin')  # 2
)

CONTRAT_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('CDD', 'CDD'),  # 1
    ('CDI', 'CDI')  # 2
)

TYPE_OPERATION_CAISSE_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Recette', 'Recette'),  # 1
    ('Dépense', 'Dépense')  # 2
)

CATEGORIE_DEPENSE_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Salaires', 'Salaires'),  # 1
    ('Charges locatives', 'Charges locatives'),  # 2
    ('Mobiliers et Infrastructures', 'Mobiliers et Infrastructures'),  # 3
    ('Fournitures Scolaires', 'Fournitures scolaires et de Bureau'),  # 4
    ('Autres Fournitures', 'Autres fournitures'),  # 5
    ('Investissements', 'Investissements'),  # 6
    ('Amortissements', 'Amortissements'),  # 7
    ('Charges Recurrentes', 'Charges récurrentes'),  # 8
    ('Créances', 'Créances'),  # 9
    ('Dettes', 'Dettes'),  # 10
    ('Autres Charges', 'Autres charges'),  # 11
    ('Scolarité', 'Scolarité'),  # 12
    ('Cours Revision', 'Cours révision'),  # 13
    ('Cours Coraniques', 'Cours coraniques'),  # 14
    ('Arriere Scolaire', 'Arriere scolaire'),  # 15
    ('Remboursement Prêt', 'Remboursement prêt'),  # 16
    ('Divers', 'Divers'),  # 17
    ('Autres Recettes', 'Autres recettes')  # 18
)

TYPE_PAIEMENT_MENSUALITE_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),
    ('Scolarite', 'Scolarité'),
    ('Cours Revision', 'Cours révision'),
    ('Cours Coraniques', 'Cours coraniques'),
    ('Arriere Scolaire', 'Arriere scolaire')
)

MOIS_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),
    ('janvier', 'janvier'),
    ('fevrier', 'fevrier'),
    ('mars', 'mars'),
    ('avril', 'avril'),
    ('mai', 'mai'),
    ('juin', 'juin'),
    ('juillet', 'juillet'),
    ('aout', 'aout'),
    ('septembre', 'septembre'),
    ('octobre', 'octobre'),
    ('novembre', 'novembre'),
    ('decembre', 'decembre')
)

TRIMESTRE_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),
    ('MP', 'Maternelle/Primaire'),
    ('1er trimestre', '1er trimestre'),
    ('2ème trimestre', '2ème trimestre'),
    ('3ème trimestre', '3ème trimestre'),
    ('CLGE', 'Collège/Lycée'),
    ('1er semestre', '1er semestre'),
    ('2ème semestre', '2ème semestre')

)

REGIME_CORANIQUE_CHOICES = (
    ('Selectionnez', 'Sélectionnez'),  # 0
    ('Internat', 'Internat'),  # 1
    ('Externat', 'Externat')  # 2
)


class AnneeScolaire(models.Model):
    descript_annee = models.CharField(max_length=10)

    def __str__(self):
        return self.descript_annee


class Matiere(models.Model):
    nom_matiere = models.CharField(max_length=50)
    coeff = models.IntegerField(default=1)

    def __str__(self):
        return '{} {} '.format(self.nom_matiere, self.coeff)


class Personnel(models.Model):
    nom_personnel = models.CharField(max_length=30)
    prenom_personnel = models.CharField(max_length=50)
    civilite = models.CharField(max_length=15, default='Selectionnez', choices=CIVILITE_CHOICES)
    date_naissance = models.DateField()
    niveau_etude = models.CharField(max_length=50)
    type_personnel = models.CharField(max_length=15, default='Selectionnez', choices=TYPE_PERSONNEL)
    adresse_personnel = models.CharField(max_length=50)
    contact_personnel = models.CharField(max_length=25)
    fonction_personnel = models.CharField(max_length=35)
    email_personnel = models.EmailField()
    sexe_personnel = models.CharField(max_length=15, default='Selectionnez', choices=SEXE_PERSONNEL)
    salbase = models.DecimalField(max_digits=10, decimal_places=2)
    annee_experience = models.CharField(max_length=10)
    contrat_type = models.CharField(max_length=15, default='Selectionnez', choices=CONTRAT_CHOICES)
    diplome = models.CharField(max_length=25)
    date_embauche = models.DateField()

    def __str__(self):
        return '{} | {} | {} | {}'.format(self.nom_personnel, self.prenom_personnel, self.contact_personnel,
                                          self.type_personnel)


class Cours(models.Model):
    nbre_heure_cour = models.IntegerField()
    jour = models.CharField(max_length=10)
    heure_debut = models.TimeField(auto_now=True)
    heure_fin = models.TimeField(auto_now=True)
    idpersonnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)
    idmatiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {}'.format(self.idpersonnel, self.idmatiere, self.nbre_heure_cour, self.jour)

    @property
    def enseignant(self):
        return self.idpersonnel

    @property
    def matiere(self):
        return self.idmatiere


class Absence(models.Model):
    nbre_heure_absence = models.IntegerField()
    motif_absence = models.CharField(max_length=50)
    type_motif = models.CharField(max_length=20)
    date_absence = models.DateField()
    mois_absence = models.CharField(max_length=15, default='Selectionnez', choices=MOIS_CHOICES)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    idcours = models.ForeignKey(Cours, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {}'.format(self.idcours, self.motif_absence, self.date_absence, self.mois_absence)

    @property
    def cours(self):
        return self.idcours

    @property
    def annee(self):
        return self.annee_scolaire


class AvanceSalaire(models.Model):
    montant_avance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    intitule = models.TextField()
    date_avance = models.DateField(auto_now=True)
    mois_avance = models.CharField(max_length=15, default='Selectionnez', choices=MOIS_CHOICES)
    anscolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    idpersonnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {} '.format(self.idpersonnel, self.intitule, str(self.montant_avance), self.mois_avance)

    @property
    def personnel(self):
        return self.idpersonnel

    @property
    def annee(self):
        return self.anscolaire


class Caisse(models.Model):
    libelle_operation = models.TextField()
    montant_encaisse = models.DecimalField(max_digits=15, decimal_places=2)
    type_operation = models.CharField(max_length=15, default='Selectionnez', choices=TYPE_OPERATION_CAISSE_CHOICES)
    date_operation = models.DateField(auto_now=True)
    solde_actuel = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    heure_operation = models.TimeField(auto_now=True)
    qte = models.IntegerField(null=True, default=0)
    pua = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    provient = models.CharField(max_length=50, null=True)
    destine = models.CharField(max_length=50, null=True)
    observ = models.CharField(max_length=90, null=True)
    anscolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    piece_jointe = models.FileField(upload_to='media/', null=True)
    categ_depense = models.CharField(max_length=100, default='Selectionnez', choices=CATEGORIE_DEPENSE_CHOICES)

    def __str__(self):
        return '{} {} {} '.format(self.libelle_operation, str(self.montant_encaisse), self.type_operation)

    @property
    def annee(self):
        return self.anscolaire


class ContratTravail(models.Model):
    date_debut = models.DateField(auto_now=True)
    date_fin = models.DateField(auto_now=True)
    periode_essai = models.CharField(max_length=10)
    thoraire = models.DecimalField(max_digits=10, decimal_places=2)
    salfixe = models.DecimalField(max_digits=10, decimal_places=2)
    duree_contrat_chiffre = models.IntegerField(default=1)
    duree_contrat_lettre = models.CharField(max_length=50)
    date_signature_contrat = models.DateField(auto_now=True)
    idpersonnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {} {}'.format(self.idpersonnel, self.date_debut, self.date_fin, self.periode_essai,
                                       self.duree_contrat_lettre)

    @property
    def personnel(self):
        return self.idpersonnel


class Eleve(models.Model):
    matricule = models.CharField(max_length=15, primary_key=True, unique=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe_eleve = models.CharField(max_length=15, default='Selectionnez', choices=SEXE_ELEVE)
    pere = models.CharField(max_length=50)
    mere = models.CharField(max_length=50, default='')
    tuteur = models.CharField(max_length=50)
    contact_parent = models.CharField(max_length=25)
    adresse = models.CharField(max_length=50)
    ecole_origine = models.CharField(max_length=50)
    photo_eleve = models.FileField(upload_to='media/photoeleve/', null=True)
    datenaissance = models.DateField()
    lieu_naissance = models.CharField(max_length=50)
    date_arrivee = models.DateField()
    date_depart = models.DateField(null=True)
    depart = models.BooleanField(default=False)
    pays_naissance = models.CharField(max_length=70)

    def __str__(self):
        return self.matricule


class CycleScolaire(models.Model):
    cycle = models.CharField(max_length=15, default='Selectionnez', choices=CYCLE_CHOICES)

    def __str__(self):
        return self.cycle


class Classe(models.Model):
    nom_classe = models.CharField(max_length=20)
    frais_inscription = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frais_reinscription = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frais_scolarite = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tranche1 = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tranche2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    tranche3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    idcycle = models.ForeignKey(CycleScolaire, on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.nom_classe)

    @property
    def cycle(self):
        return self.idcycle


class Salaire(models.Model):
    date_paiement = models.DateField(auto_now=True)
    nbre_heure = models.IntegerField(default=0)
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    mois_paie = models.CharField(max_length=15, default='Selectionnez', choices=MOIS_CHOICES)
    detail_paiement = models.TextField()
    taux_horaire = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avance_paie = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    primes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salbrut = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cotis_sociale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salnet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nb_hsupp = models.IntegerField(default=0)
    mont_hsupp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    idpersonnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.idpersonnel, self.detail_paiement, self.mois_paie)

    @property
    def enseignant(self):
        return self.idpersonnel

    @property
    def annee(self):
        return self.anneescolaire


class Discipline(models.Model):
    motif_sanction = models.TextField()
    sanction = models.CharField(max_length=80)
    observation = models.TextField()
    annescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    date_sanction = models.DateField()
    delit = models.TextField()
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {}'.format(self.mateleve, self.motif_sanction, self.sanction, self.delit)

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.annescolaire


class Ecole(models.Model):
    nom_ecole = models.CharField(max_length=50)
    ville_ecole = models.CharField(max_length=20)
    agrement_ecole = models.CharField(max_length=15)
    prefect_commune = models.CharField(max_length=15)
    bp_ecole = models.CharField(max_length=15, null=True)
    telephone1 = models.CharField(max_length=20)
    telephone2 = models.CharField(max_length=20, null=True)
    email_ecole = models.EmailField()
    site_internet = models.URLField(null=True)
    devise_ecole = models.CharField(max_length=50)
    logo_ecole = models.FileField(upload_to='media/', null=True, blank=True)
    dsee = models.CharField(max_length=30)
    dg = models.CharField(max_length=50)
    coordo_primaire = models.CharField(max_length=50, null=True)
    coordo_secondaire = models.CharField(max_length=50, null=True, blank=True)
    comptable = models.CharField(max_length=50, null=True)
    signa_dg = models.FileField(upload_to='media/', null=True, blank=True)
    signa_de = models.FileField(upload_to='media/', null=True, blank=True)

    def __str__(self):
        return '{} {} {} '.format(self.nom_ecole, self.ville_ecole, self.telephone1)


class EtatPaiementCoran(models.Model):
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    inscription = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    m_rabais = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjanvier = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    ffevreir = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fmars = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    favril = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fmai = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjuin = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjuillet = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    faout = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fseptembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fnovembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fdecembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.mateleve, self.inscription)

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire


class EtatPaiementRevision(models.Model):
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    inscription = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    m_rabais = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjanvier = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    ffevreir = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fmars = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    favril = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fmai = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjuin = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjuillet = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    faout = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fseptembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fnovembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fdecembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.mateleve, self.inscription)

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire


class EtatPaiementScolarite(models.Model):
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    inscription = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    m_rabais = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjanvier = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    ffevreir = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fmars = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    favril = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fmai = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjuin = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fjuillet = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    faout = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fseptembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fnovembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    fdecembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.mateleve, self.inscription)

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire


class Evaluation(models.Model):
    note1 = models.FloatField(default=0)
    note2 = models.FloatField(default=0)
    note3 = models.FloatField(default=0)
    mois_evaluation = models.CharField(max_length=15, default='Selectionnez', choices=MOIS_CHOICES)
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    trimestre = models.CharField(max_length=15, default='Selectionnez', choices=TRIMESTRE_CHOICES)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)
    idmatiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {} {} '.format(self.mateleve, self.mois_evaluation, self.trimestre, str(self.note1),
                                        str(self.note2))

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def matiere(self):
        return self.idmatiere

    @property
    def annee(self):
        return self.anneescolaire


class Historique(models.Model):
    user_login = models.CharField(max_length=20)
    nature_operation = models.CharField(max_length=30)
    detail_operation = models.TextField()
    date_operation = models.DateField(auto_now=True)
    heure_op = models.TimeField(auto_now=True)

    def __str__(self):
        return '{} {} {} '.format(self.user_login, self.detail_operation, self.date_operation)


class Inscription(models.Model):
    date_inscription = models.DateField(auto_now=True)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    etat_inscription = models.CharField(max_length=10, default='Inscrit')
    regime_coran = models.CharField(max_length=20, choices=REGIME_CORANIQUE_CHOICES,
                                    default=REGIME_CORANIQUE_CHOICES[1][0])
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idcycle = models.ForeignKey(CycleScolaire, on_delete=models.CASCADE, null=True)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} '.format(self.mateleve, self.idclasse, self.etat_inscription)

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse.nom_classe

    @property
    def annee(self):
        return self.annee_scolaire

    @property
    def cycle(self):
        return self.idcycle.cycle


class PaiementCoran(models.Model):
    mois_paye = models.CharField(max_length=15, default='Selectionnez', choices=MOIS_CHOICES)
    date_payement = models.DateField(auto_now=True)
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    detail = models.TextField()
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mont_du = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reste_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {}'.format(self.mateleve, self.mois_paye, self.date_payement, str(self.montant_paye))

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire


class PaiementRevision(models.Model):
    mois_paye = models.CharField(max_length=15, default='Selectionnez', choices=MOIS_CHOICES)
    date_payement = models.DateField(auto_now=True)
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    detail = models.TextField()
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mont_du = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reste_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {} '.format(self.mateleve, self.mois_paye, self.date_payement, str(self.montant_paye))

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire


class PaiementScolarite(models.Model):
    mois_paye = models.CharField(max_length=15, default='Selectionnez', choices=MOIS_CHOICES)
    date_payement = models.DateField(auto_now=True)
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    detail = models.TextField()
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mont_du = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reste_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tranche_paye = models.CharField(max_length=25)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {}'.format(self.mateleve, self.mois_paye, self.date_payement, self.montant_paye)

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire


class ResultatTrimestre(models.Model):
    trimes = models.CharField(max_length=15)
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    mgenerale = models.FloatField(default=0)
    mcours = models.FloatField(default=0)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} '.format(self.mateleve, self.trimes, str(self.mgenerale))

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.anneescolaire


class ResultatAnnuel(models.Model):
    mga = models.FloatField(default=0)
    annes = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    mateleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    idclasse = models.ForeignKey(Classe, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.mateleve, str(self.mga))

    @property
    def eleve(self):
        return self.mateleve

    @property
    def classe(self):
        return self.idclasse

    @property
    def annee(self):
        return self.annes
