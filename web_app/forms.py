from django import forms as f
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from web_app import models as m


TYPES = (
    (1, 'mięsny'),
    (2, 'wegetariański'),
    (3, 'wegański')
)


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


class UserUpdateForm(UserCreateForm):
    password = None
    password2 = None


class UserUpdatePasswordForm(f.Form):
    new_password = f.CharField(label='Wprowadź nowe hasło' ,widget=f.PasswordInput)
    new_password2 = f.CharField(label='Ponownie wprowadź nowe hasło', widget=f.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password') != cleaned_data.get('new_password2'):
            raise ValidationError('Podane hasła nie są jednakowe')


class PlanAddForm(f.Form):
    name = f.CharField(max_length=64, label='Nazwa planu')
    type = f.ChoiceField(choices=TYPES, label='Typ planu')
    persons = f.IntegerField(label='Dla ilu osób')
    meal = f.ModelMultipleChoiceField(queryset=m.Meal.objects.filter(), widget=f.CheckboxSelectMultiple, label='Dania:')
