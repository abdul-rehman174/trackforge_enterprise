from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password

from .models import CustomUser


class SignupForm(UserCreationForm):
    """Self-service signup. Always lands the user with role='user'."""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False, max_length=150)
    last_name = forms.CharField(required=False, max_length=150)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.help_text = ""

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.role = "user"
        if commit:
            user.save()
        return user


class CustomUserForm(forms.ModelForm):
    """Admin-managed user form. Password is optional on update."""

    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text="Leave blank to keep the existing password.",
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "first_name", "last_name", "role"]

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        if pwd:
            validate_password(pwd, self.instance)
        return pwd

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
