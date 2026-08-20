from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import Utilisateur, NIVEAU_ACCES_CHOICES
from django.core.exceptions import ValidationError

class ConnexionForm(AuthenticationForm):
    username = forms.EmailField(
       widget=forms.EmailInput(attrs={'id':'idemail','placeholder': ' ', 'class': 'form-control floating-input', 'autofocus': True})
    )
    password = forms.CharField(
       widget=forms.PasswordInput(attrs={'id':'idpassword', 'placeholder': ' ', 'class': 'form-control floating-input'})
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
            'password1': forms.PasswordInput(attrs={'class':'form-control','title':'Tapez un mot de passe d\'au moins 8 caractères composé de lettres, chiffres, majuscules, minuscule et de caractères spéciaux'}),
            'password2': forms.PasswordInput(attrs={'class':'form-control','title':'Retapez le même mot de passe'}),
            'photo_profil' : forms.FileInput(attrs={'class': 'd-none', 'accept': 'image/*','title': 'Importez une photo de profil','id':'id_photo_user', 'onchange': 'previewPhotoProfil(this)'}),
            'niveau_acces' : forms.Select(attrs={'class':'form-control','title':'Sélectionnez le niveau d\'accès de l\'utilisateur'}, choices=NIVEAU_ACCES_CHOICES)
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Les deux mots de passe ne correspondent pas.', code='password_mismatch')
        return password2
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photo_profil'].required = False
        self.fields['username'].help_text = 'Tapez un nom utilisateur sans espace d\'au plus 150 caractères contenant lettres, chiffres, et @/./+/-/_'  # ou ton propre texte
        self.fields['password1'].help_text = 'Au moins 8 caractères, avec lettres, chiffres et caractères spéciaux'
        self.fields['password2'].help_text = 'Confirmer le mot de passe en le retapant à nouveau'

        self.fields['password1'].widget.attrs.update({'placeholder': 'Mot de passe'}) # Permet de définir un placeholder pour la zone de saisie password1
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirmation du mot de passe'}) # Permet de définir un placeholder pour la zone de saisie password2