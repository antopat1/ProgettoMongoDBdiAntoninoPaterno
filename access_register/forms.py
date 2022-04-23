from django import forms
from django.contrib.auth.models import User


class FormRegistrazionUser(forms.ModelForm):

    username = forms.CharField(widget=forms.TextInput())
    email = forms.CharField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())
    conferma_password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ["username", "email", "password", "conferma_password"]

    def clean(self):  # metodo per validare i dati, nello specifico le due password coincidenti
        super().clean()
        password = self.cleaned_data["password"]
        password_confirm = self.cleaned_data["conferma_password"]
        if password != password_confirm:
            raise forms.ValidationError("Le password non combaciano")
        return self.cleaned_data
