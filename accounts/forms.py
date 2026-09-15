import re

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'full_name', 'irish_mobile_number')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'full_name', 'irish_mobile_number')

def validate_irish_mobile(value):
    if not value.startswith('08'):
        raise ValidationError('Irish mobile numbers must start with 08.')
    # format length check (08X XXXXXXX -> 10 digits)
    digits_only = re.sub(r'\D', '', value)
    if len(digits_only) != 10:
        raise ValidationError('Irish mobile numbers must exactly have 10 digits (e.g. 08X XXXXXXX).')

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'irish_mobile_number']

    def clean_irish_mobile_number(self):
        number = self.cleaned_data.get('irish_mobile_number')
        if number:
            validate_irish_mobile(number)
            # Normalize
            return re.sub(r'\D', '', number)
        return number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        email = cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            self.add_error('email', "Email must be unique.")

        return cleaned_data

    def save_user(self, is_seller=False, is_buyer=False):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_seller = is_seller
        user.is_buyer = is_buyer
        user.save()
        return user
