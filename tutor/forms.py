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
from .models import Tutor, Subject, Review


class TutorForm(forms.ModelForm):
    """
    Main elements of the Tutor Form
    """
    rate = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': '24.00', }))
    bio = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'This is your resume. Be very descriptive and describe yourself to prospective pupils.',
               'class': 'md-textarea', 'maxlength': Tutor.BIO_MAX_LENGTH}))

    class Meta:
        model = Tutor
        fields = ('rate', 'bio')


class SubjectForm(forms.ModelForm):
    """
    Subject for a tutor - used as a seperate class here to be deployed in a formset
    """
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Geometry',
                                                         'required': 'true'}))

    class Meta:
        model = Subject
        fields = ('name',)


class ReviewForm(forms.ModelForm):
    """
    Review for a tutor
    """
    text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Write your review here',
                                                        'class': 'md-textarea', 'maxlength': Review.TEXT_MAX_LENGTH, }))

    class Meta:
        model = Review
        fields = ('rating', 'text', 'anonymous')

    def save(self, commit=True, *args, **kwargs):
        """
        Custom save to take in tutor and user as kwargs
        :return: instance of the saved Review
        """
        instance = super(ReviewForm, self).save(commit=False)
        instance.tutor = kwargs.pop('tutor')
        instance.user = kwargs.pop('user')
        if commit:
            instance.save()
            self.save_m2m()
        return instance
