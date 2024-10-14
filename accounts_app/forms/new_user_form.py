from django import forms
from accounts_app.models import User


class NewUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password"]