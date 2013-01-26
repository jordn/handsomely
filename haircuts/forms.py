from django import forms

class RegisterForm(forms.Form):
	email = forms.EmailField(required=True, label='', widget=forms.TextInput( \
			attrs={'placeholder': 'email@address.com', 'autofocus': 'autofocus'}))


class LoginForm(forms.Form):
	email = forms.EmailField(required=True, label='', widget=forms.TextInput(attrs={'placeholder': 'email@address.com', 'autofocus': 'autofocus'}))
	password = forms.CharField(required=True, label='', widget=forms.PasswordInput(attrs={'placeholder': 'password'}))
	remember_me = forms.BooleanField(label='Remember Me')