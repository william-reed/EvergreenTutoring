from django.contrib.auth.models import User
from .models import Profile
from django import forms


class UserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=20, required=True)
    last_name = forms.CharField(max_length=20, required=True)
    username = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class ProfileForm(forms.ModelForm):
    street_address = forms.CharField(max_length=40, required=True)
    city = forms.CharField(max_length=20, required=True)
    state = forms.CharField(max_length=20, required=True)
    zip = forms.IntegerField(min_value=1000, max_value=99999, required=True)

    class Meta:
        model = Profile
        fields = ('street_address', 'city', 'state', 'zip')


class EditAccountForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=True)
    last_name = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)
    street_address = forms.CharField(max_length=40, required=True)
    city = forms.CharField(max_length=20, required=True)
    state = forms.CharField(max_length=20, required=True)
    zip = forms.IntegerField(max_value=99999, required=True)

    class Meta:
        fields = ('first_name', 'last_name', 'email', 'street_address', 'city', 'state', 'zip')
