# -*- coding: utf-8 -*-
import re

from django import forms
from django.template.defaultfilters import safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from models import User


class EditProfileForm(forms.ModelForm):
    """
    EditProfileForm

    """

    class Meta:
        model = User
        fields = ('full_name', 'gender', 'join_mailing_list', )

        widgets = {
            'full_name': forms.TextInput(attrs={'required': '', 'class': 'input-xxlarge'}),
        }
        field_args = {
            'full_name': {
                'error_messages': {
                    'required': _('Full name is required')
                }
            },
            'username': {
                'error_messages': {
                    'required': _('Username address is required')
                },
                'help_text': ''
            },
        }

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.get('request')
            kwargs.pop('request')

        super(EditProfileForm, self).__init__(*args, **kwargs)

        # required fields to over-ride model
        self.fields['full_name'].required = True

        self.fields['full_name'].widget.attrs.update({'class': 'form-control'})


    def all_fields(self):
        return [field for field in self if not field.is_hidden and field.name not in ('terms', 'captcha')]

    def clean(self):
        cleaned_data = super(EditProfileForm, self).clean()
        return cleaned_data


class SocialForm(forms.Form):
    """

    """
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-xlarge', 'placeholder': 'Full name...', 'required': ''}))
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'input-xlarge', 'placeholder': 'Email address...', 'required': ''}))
    join_mailing_list = forms.BooleanField(required=False, widget=forms.CheckboxInput(
        attrs={'tabindex': '4', 'class': 'field login-checkbox'}),
                                           label=_('Join a mailing list for your interests'))
    terms = forms.BooleanField(widget=forms.CheckboxInput(attrs={'tabindex': '4', 'class': 'field login-checkbox'}),
                               label=_('I have read and agree with the Terms of Use.'),
                               error_messages={'required': _('Your must agree for the terms and conditions')})

    def __init__(self, *args, **kwargs):
        super(SocialForm, self).__init__(*args, **kwargs)

        if re.match(r'[^@]+@[^@]+\.[^@]+', self.initial.get('email', '')):
            self.fields['email'].widget.attrs['readonly'] = True

        self.fields['email'].error_messages.update({'required': _('Email field is required')})

        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['full_name'].widget.attrs.update({'class': 'form-control'})

    def all_fields(self):
        return [field for field in self if not field.is_hidden and field.name not in ('terms', 'join_mailing_list')]

    def clean(self):
        cleaned_data = super(SocialForm, self).clean()

        # validate email unique
        try:
            User.objects.get(email=str(cleaned_data.get('email', None)).lower())
            self._errors['email'] = self.error_class(
                [_(safe('Your email already exists, please use different email address. '))])
            del cleaned_data['email']
        except User.DoesNotExist:
            pass

        return cleaned_data

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'username', 'date_of_birth', 'full_name', 'is_superuser', 'is_staff',
                  'is_active', 'groups', 'user_permissions', 'last_login', 'threshold', 'gender')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'date_of_birth', 'full_name', 'is_superuser',
                  'is_staff', 'is_active', 'groups', 'user_permissions', 'last_login', 'threshold', 'gender']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]