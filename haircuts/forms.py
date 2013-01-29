from django import forms
from models import Notification

class RegisterForm(forms.Form):
	email = forms.EmailField(required=True, label='', widget=forms.TextInput( \
			attrs={'placeholder': 'email@address.com', 'autofocus': 'autofocus'}))


class LoginForm(forms.Form):
	email = forms.EmailField(required=True, label='', widget=forms.TextInput(attrs={'placeholder': 'email@address.com', 'autofocus': 'autofocus'}))
	password = forms.CharField(required=True, label='', widget=forms.PasswordInput(attrs={'placeholder': 'password'}))
	remember_me = forms.BooleanField(required=False, label='Remember Me')

class NotifyForm(forms.Form):
	gender_choices = (('M', 'Male'), ('F','Female'))
	gender = forms.ChoiceField(gender_choices, required=True)
	day_choices = (('TODAY', 'Today'), ('TOMORROW','Tomorrow'), ('TDA','The Day After'))
	day = forms.ChoiceField(day_choices, required=True)
	time_choices = (
		('0800', '0800'),
		('0815', '0815'),
		('0830', '0830'),
		('0845', '0845'),
		('0900', '0900'),
		('0915', '0915'),
		('0930', '0930'),
		('0945', '0945'),
		)
	time = forms.ChoiceField(time_choices, required=True)
	original_price = forms.FloatField(required=True, label='', widget=forms.TextInput(attrs={'placeholder': 'Original Price', 'autofocus': 'autofocus'}))
	discounted_price = forms.FloatField(required=True, label='', widget=forms.TextInput(attrs={'placeholder': 'Original Price', 'autofocus': 'autofocus'}))
