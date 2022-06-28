from django import forms as f
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class LoginForm(f.Form):
    username = f.CharField(label='Użytkownik')
    password = f.CharField(label='Hasło', widget=f.PasswordInput)


class UserCreateForm(f.Form):
    username = f.CharField(label='Nazwa Użytkownika *')
    password = f.CharField(label='Hasło *', widget=f.PasswordInput)
    password2 = f.CharField(label='Powtórz hasło *', widget=f.PasswordInput)
    first_name = f.CharField(label='Imię', max_length=64, required=False)
    last_name = f.CharField(label='Nazwisko', max_length=64, required=False)
    email = f.EmailField(label='Adres e-mail', required=False)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password != password2:
            raise ValidationError('Podane hasła nie są jednakowe')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user = User.objects.filter(username=username)
        if user:
            raise ValidationError('Użytkownik o podanej nazwie już istnieje')
