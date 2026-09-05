from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=80, label="Ad")
    last_name = forms.CharField(max_length=80, label="Soyad")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=20, required=False, label="Telefon")
    password = forms.CharField(widget=forms.PasswordInput, label="Şifrə")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Şifrə (təkrar)")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu email artıq qeydiyyatdan keçib.")
        return email

    def clean_phone(self):
        raw = (self.cleaned_data.get("phone") or "").strip()
        if not raw:
            return ""
        digits = "".join(ch for ch in raw if ch.isdigit())
        if digits.startswith("994"):
            digits = digits[3:]
        if digits.startswith("0"):
            digits = digits[1:]
        if digits and len(digits) < 7:
            raise forms.ValidationError("Telefon nömrəsi düzgün deyil.")
        return f"+994{digits}" if digits else ""

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirm = cleaned.get("password_confirm")
        if password and confirm and password != confirm:
            self.add_error("password_confirm", "Şifrələr eyni deyil.")
        if password:
            try:
                validate_password(password)
            except DjangoValidationError as exc:
                self.add_error("password", exc)
        return cleaned


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Şifrə")


class OTPForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6, label="OTP kod")
