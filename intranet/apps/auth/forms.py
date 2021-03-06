# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class AuthenticateForm(AuthenticationForm):

    """Implements a login form.

    Attributes:
        - username -- The username text field.
        - password -- The password text field.

    """
    username = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Username"}), error_messages={"required": "Invalid username"})
    password = forms.CharField(required=True, widget=forms.widgets.PasswordInput(attrs={"placeholder": "Password"}), error_messages={"required": "Invalid password"})

    def is_valid(self):
        """Validates the username and password in the form"""
        form = super(AuthenticateForm, self).is_valid()

        for f, error in self.errors.iteritems():
            if f != "__all__":
                self.fields[f].widget.attrs.update({"class": "error", "placeholder": strip_tags(error)})
            else:
                self.fields["password"].widget.attrs.update({"class": "error", "placeholder": "Invalid password"})

        return form
