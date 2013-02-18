# This python file uses the following encoding: utf-8 # Needed to have a pound sign show up
from django import forms
from models import Notification, Request
from django.contrib.auth.models import User
from django.forms import Form, ModelForm #ModelForm helps create forms that closely follow models

class RegisterForm(Form):
    """
    A form that creates a (django) user, which is yet to be validated. Nb. to create a handsomely user at the same time.
    """
    error_messages = {
        'duplicate_username': ("That email has already been registered."),
    }

    email = forms.EmailField(required=True, label='', max_length=30, widget=forms.TextInput( \
            attrs={'placeholder': 'email@address.com', 'autofocus': 'autofocus'})) #emaisl are often longer than 30 chars :( but limited by username field atm

    def clean_email(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["email"]
        try: #£ sign after @ is slipping through the net
            assert(pound not in username)
        except AssertionError:
            raise forms.ValidationError(self.error_messages['pound_sign_found'])
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

class LoginForm(Form):
    email = forms.EmailField(required=True, label='', widget=forms.TextInput(attrs={'placeholder': 'email@address.com', 'autofocus': 'autofocus'}))
    password = forms.CharField(required=True, label='', widget=forms.PasswordInput(attrs={'placeholder': 'password'}))
    remember_me = forms.BooleanField(required=False, label='Remember Me')


class RequestForm(ModelForm):
    """Handles taking in the request by a certain user for a certain haircut at a certain salon"""
    class Meta:
        model = Request


class NotifyForm(Form):
    gender_choices = (('M', 'Male'), ('F','Female'))
    gender = forms.ChoiceField(gender_choices, required=True)
    day_choices = (('TODAY', 'Today'), ('TOMORROW','Tomorrow'), ('TDA','The Day After'))
    day = forms.ChoiceField(day_choices, required=True)
    time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs= {'placeholder': 'In format HH:MM'}))
    original_price = forms.FloatField(required=True, label='', widget=forms.TextInput(attrs={'placeholder': 'Original Price', 'autofocus': 'autofocus'}))
    discounted_price = forms.FloatField(required=True, label='', widget=forms.TextInput(attrs={'placeholder': 'Original Price', 'autofocus': 'autofocus'}))
    notes = forms.CharField(max_length = 100 , widget=forms.TextInput(attrs={'placeholder': '100 characters maximum', 'autofocus': 'autofocus'}))