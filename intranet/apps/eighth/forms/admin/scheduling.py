# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from ...models import EighthScheduledActivity


class ScheduledActivityForm(forms.ModelForm):

    """Represents a row in the table activity scheduling admin page"""

    # Whether the activity should actually scheduled for the block
    scheduled = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(ScheduledActivityForm, self).__init__(*args, **kwargs)

        for fieldname in ["sponsors", "rooms"]:
            self.fields[fieldname].help_text = None

        for fieldname in ["block", "activity"]:
            self.fields[fieldname].widget = forms.HiddenInput()

    def validate_unique(self):
        # We'll handle this ourselves by updating if already exists
        pass

    class Meta:
        model = EighthScheduledActivity
        fields = ["scheduled",
                  "block",
                  "activity",
                  "rooms",
                  "capacity",
                  "sponsors",
                  "comments"]
        widgets = {
            "capacity": forms.TextInput(),
            "comments": forms.Textarea(attrs={"rows": 2, "cols": 30})
        }
