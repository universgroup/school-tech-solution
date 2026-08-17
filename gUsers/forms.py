from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import Utilisateur


class ConnexionForm(AuthenticationForm):
    username = forms.EmailField(
       widget=forms.EmailInput(attrs={'id':'idemail','placeholder': 'Email', 'class': 'form-control', 'autofocus': True})
    )
    password = forms.CharField(
       widget=forms.PasswordInput(attrs={'id':'idpassword', 'placeholder': 'Mot de passe', 'class': 'form-control'})
    )


class CreationUtilisateurForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email','password1','password2', 'photo_profil', 'niveau_acces']
        labels = {
            'username': 'Nom utilisateur',
            'first_name': 'Prénom(s)',
            'last_name': 'Nom',
            'email': 'Adresse email',
            'password1': 'Mot de passe',
            'password2' : 'Confirmation du mot de passe',
            'photo_profil': 'Photo',
            'niveau_acces': 'Niveau d\'accès'
        }
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control','placeholder':'Nom utilisateur','title':'Tapez votre nom d\'utilisateur'}),
            'first_name': forms.TextInput(attrs={'class':'form-control','placeholder':'Prénom(s)', 'title':'Tapez votre prénom(s)'}),
            'last_name': forms.TextInput(attrs={'class':'form-control','placeholder':'Nom famille', 'title':'Tapez votre nom de famille'}),
            'email': forms.EmailInput(attrs={'class':'form-control','placeholder': 'Ex: contact@universtechgroup.com','pattern': "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\'.[a-zA-Z]{2,}", 'title': 'Saisissez un email correct!'}),
            'photo_profil' : forms.FileInput(attrs={'class': 'd-none', 'accept': 'image/*','title': 'Importez une photo de profil','id':'id_photo_user'}),
            'niveau_acces' : forms.Select(attrs={'class':'form-control','title':'Sélectionnez le niveau d\'accès de l\'utilisateur'}, choices=Utilisateur.NIVEAU_ACCES_CHOICES)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photo_profil'].required = False


class ModificationUtilisateurForm(UserChangeForm):
    password = None   # on retire le champ mot de passe (haché) de ce formulaire de modification

    class Meta:
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email', 'photo_profil', 'niveau_acces']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for nom_champ, champ in self.fields.items():
        #     champ.widget.attrs['class'] = 'form-control'