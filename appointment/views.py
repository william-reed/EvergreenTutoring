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

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tutor.decorators import tutors_only
from .models import Appointment
from tutor.models import Tutor
from datetime import datetime, date
from pytz import timezone
from django.views import generic
from .forms import AvailabilityForm
from evergreen import settings


@login_required
def index(request):
    if request.user.profile.is_tutor():
        return render(request, 'appointment/appointment_list_tutor.html',
                      {'object_list': request.user.profile.all_appointments()})
    else:
        return render(request, 'appointment/appointment_list_user.html',
                      {'object_list': request.user.profile.all_appointments()})


# TODO: provide link to this from tutor control panel or something
@login_required
@tutors_only
def create_availability(request):
    context = {}
    if request.method == "POST":
        availability_form = AvailabilityForm(request.POST)
        if availability_form.is_valid():
            date = availability_form.cleaned_data.get('date')
            start_time = availability_form.cleaned_data.get('start_time')
            end_time = availability_form.cleaned_data.get('end_time')
            location_choice = availability_form.cleaned_data.get('location_choice')
            tutor_comments = availability_form.cleaned_data.get('tutor_comments')
            other_location = None

            if location_choice == "OTHER":
                other_location = availability_form.cleaned_data.get('other_location')

            tutor = Tutor.objects.get(user=request.user)
            duration = (datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)).seconds / 60
            start_time = timezone(tutor.user.profile.timezone).localize(datetime.combine(date, start_time))

            location = None

            if location_choice == 'TUTOR_ADDRESS':
                location = tutor.user.profile.address()
            elif location_choice == 'USER_ADDRESS':
                # dummy data for the map
                location = "United States"
            elif location_choice == 'OTHER':
                location = other_location

            appointment = Appointment(tutor=tutor, start_time=start_time, duration=duration, location=location,
                                      location_option=location_choice, tutor_comments=tutor_comments)

            # if it overlaps with a previously created appointment send an 'error_message'
            appointments = Appointment.objects.filter(tutor=tutor)
            for app in appointments:
                if app.overlap(appointment):
                    context['error_message'] = 'Appointment for ' + start_time.strftime(
                        settings.DATE_FORMAT + ' at ' + settings.TIME_FORMAT) + \
                                               ' cannot be created. It overlaps with a previously created appointment.'
                    return render(request, 'appointment/appointment_create.html', context)

            # success
            appointment.save()
            context['success_message'] = \
                'Appointment for ' + start_time.strftime(settings.DATE_FORMAT +
                                                         ' ' + settings.TIME_FORMAT) + ' has been created!'
    else:
        availability_form = AvailabilityForm

    context['availability_form'] = availability_form
    return render(request, 'appointment/appointment_create.html', context)


# DetailView for a tutor
# login is required for this (Set in urls)
class DetailView(generic.DetailView):
    model = Appointment
    USER_TEMPLATE = 'appointment/appointment_detail_user.html'
    OWNER_TEMPLATE = 'appointment/appointment_detail_tutor.html'
    USER_TEMPLATE_BOOKED = 'appointment/appointment_detail_user_booked.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        app = self.object

        # if its in a state where it can't change ignore this stuff
        if app.status == "CANCELED" or app.status == "EXPIRED" or app.status == "COMPLETED":
            return self.render_to_response(context=super(DetailView, self).get_context_data(**kwargs))

        context = super(DetailView, self).get_context_data(**kwargs)

        # tutor
        tutor = self.request.user.profile.is_tutor()

        # differentiate between user requesting, tutor accepting, or tutor canceling
        # if the owner is posting to this
        if tutor and tutor == app.tutor:
            #  accept
            if request.POST.get('accept', False):
                app.accept()
                context['success_message'] = 'The appointment request has been accepted!'
            # decline
            elif request.POST.get('decline', False):
                app.decline()
                context['success_message'] = 'The appointment request has been declined.'
            # canceling
            elif request.POST.get('cancel', False):
                app.cancel_tutor()
                context['success_message'] = 'The appointment has been cancelled.'
        # if not a tutor posting, its a user:
        else:
            # no user here, so someone must be requesting it
            if not app.user:
                if request.POST.get('request', False):
                    app.request(request.user)
                    # additional comments
                    app.user_comments = request.POST.get('user_comments', None)
                    app.save()
                    context['success_message'] = 'The appointment has been requested!'
            # user wants to alter their requested / booked appointment
            elif app.user == request.user:
                if request.POST.get('cancel', False):
                    app.cancel_user()
                    context['success_message'] = 'The appointment request has been cancelled.'

        return self.render_to_response(context=context)

    def get_template_names(self):
        """
        Different templates for different types of users
        :return: the appropriate template
        """
        self.object = self.get_object()

        tutor = self.request.user.profile.is_tutor()
        # return a different view if they are the owner
        if tutor and tutor == self.object.tutor:
            return self.OWNER_TEMPLATE
        # or if they booked it
        elif self.request.user == self.object.user and self.object.status == "BOOKED":
            return self.USER_TEMPLATE_BOOKED
        # or just a normie user
        else:
            return self.USER_TEMPLATE
