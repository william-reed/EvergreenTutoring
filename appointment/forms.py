# Evergreen Tutoring - A simple online tutor scheduling service
# Copyright (C) 2017 William Reed
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from django import forms
from .models import Appointment
from evergreen import settings


# not using a model form bc some things are a little wonky and not 1-1 with the model from the form
#  including date / time
class AvailabilityForm(forms.Form):
    # following three fields are submitted using a datepicker anyway so max length is just a precaution
    date_format = [settings.DATE_FORMAT]
    date = forms.DateField(widget=forms.TextInput(attrs={'class': 'date start'}), required=True,
                           input_formats=date_format)
    time_format = [settings.TIME_FORMAT]
    start_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'time start'}), required=True,
                                 input_formats=time_format)
    end_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'time end'}), required=True,
                               input_formats=time_format)
    location_choice = forms.ChoiceField(choices=Appointment.LOCATION_CHOICES, required=True, widget=forms.RadioSelect())
    other_location = forms.CharField(max_length=80, required=False)
    tutor_comments = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Write any additional comments here',
                                                                  'class': 'md-textarea',
                                                                  'maxlength': Appointment.COMMENTS_MAX_LENGTH, }),
                                     required=False)

    class Meta:
        fields = ('date', 'start_time', 'end_time', 'location_choice', 'other_location', 'comments')

    def clean(self):
        # TODO: make sure date is in future
        cleaned_data = super(AvailabilityForm, self).clean()

        # make sure the end is after the start
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time is None or end_time is None:
            return

        if end_time <= start_time:
            msg = 'The end of the appointment must be after the start'
            self.add_error('end_time', msg)
