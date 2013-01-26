from django import forms

class RegisterForm(forms.Form):
	email = forms.EmailField(required=True, label='', widget=forms.TextInput(attrs={'placeholder': 'email@address.com', 'autofocus': 'autofocus'}))