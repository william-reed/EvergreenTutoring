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

from django.contrib import admin
from .models import Tutor, Subject, Review
from django import forms

class TutorAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(TutorAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'bio':
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield

# Register your models here.
admin.site.register(Tutor, TutorAdmin)
admin.site.register(Subject)
admin.site.register(Review)