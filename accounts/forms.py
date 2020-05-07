from django import forms
from django.contrib.auth.models import User
from .models import Profile, Preference
from datetime import datetime
from django.contrib.auth.password_validation import validate_password
from allauth.account.forms import SignupForm
from allauth.account.forms import SignupForm
from allauth.account.adapter import get_adapter


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    def clean_username(self):
        super().clean_username()
        
        value = self.cleaned_data['username']
        try:
            value.encode(encoding='utf-8').decode('ascii')
        except:
            raise forms.ValidationError("Login can only contains english letters.")
        return value

class UserForm(forms.ModelForm):
    username = forms.CharField(max_length = 100, required = True)
    password = forms.CharField(widget = forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    date_joined = forms.DateTimeField(widget = forms.HiddenInput, initial = datetime.now)
    field_order = ['first_name', 'last_name', 'username', 'email', 'password', 'confirm_password', 'date_joined']

    class Meta:
        model = User
        fields = {'first_name', 'last_name', 'username', 'email', 'password', 'confirm_password', 'date_joined'}

    def is_english(self, s):
        try:
            s.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True

    def clean(self):
        super(UserForm, self).clean()
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords does not match")

        if not first_name.isalpha():
            self._errors['first_name'] = self.error_class(['Please enter correct first name. Use only alphabetical characters (a-z, A–Z)'])

        if not last_name.isalpha():
            self._errors['last_name'] = self.error_class(['Please enter correct last name. Use only alphabetical characters (a-z, A–Z)'])

        try:
            validate_password(password)
        except forms.ValidationError as e:
            self._errors['password'] = self.error_class(e)

        del self.cleaned_data['confirm_password']
        return self.cleaned_data

class PreferenceForm(forms.ModelForm):
    class Meta:
        model = Preference
        fields = {'name'}

class ProfileCreateUpdateForm(forms.ModelForm):
    preferences = forms.ModelMultipleChoiceField(queryset=Preference.objects.all(), widget=forms.SelectMultiple)

    class Meta:
        model = Profile
        fields = ('preferences', 'image', 'is_subscribed_to_the_newsletter')


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields=('first_name', 'last_name')
