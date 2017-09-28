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

from django.test import TestCase
from django.urls import reverse
from profile.tests.user_factory import UserFactory
from tutor.tests.tutor_factory import TutorFactory
from appointment.tests.appointment_factory import AppointmentFactory
from evergreen import tests
from appointment.forms import AvailabilityForm
from appointment.models import Appointment
from evergreen import settings


class ViewTests(TestCase):
    def test_index(self):
        # not logged in check
        tests.check_not_logged_in(self, "appointment:index")

        # tutor login
        tutor = TutorFactory()
        self.client.force_login(tutor.user)
        response = self.client.get(reverse('appointment:index'))
        names = []
        for tp in response.templates:
            names.append(tp.name)
        self.assertTrue('base.html' in names)
        self.assertTrue('appointment/appointment_list.html' in names)
        self.assertTrue('appointment/appointment_list_tutor.html' in names)

        # add some appointments and  make sure they are in the object list context
        app1 = AppointmentFactory(tutor=tutor)
        app2 = AppointmentFactory(tutor=tutor, status='CANCELED')
        app3 = AppointmentFactory(tutor=tutor, user=UserFactory(), status='BOOKED')
        response = self.client.get(reverse('appointment:index'))
        object_list = response.context['object_list']
        self.assertTrue(app1 in object_list)
        self.assertTrue(app2 in object_list)
        self.assertTrue(app3 in object_list)

        # normie login
        user = UserFactory()
        self.client.logout()
        self.client.force_login(user)
        response = self.client.get(reverse("appointment:index"))
        names = []
        for tp in response.templates:
            names.append(tp.name)
        self.assertTrue('base.html' in names)
        self.assertTrue('appointment/appointment_list.html' in names)
        self.assertTrue('appointment/appointment_list_user.html' in names)

        # add some appointments and  make sure they are in the object list context
        app1 = AppointmentFactory(user=user, status='REQUESTED')
        app2 = AppointmentFactory(user=user, status='COMPLETED')
        app3 = AppointmentFactory(user=user, status='BOOKED')
        response = self.client.get(reverse('appointment:index'))
        object_list = response.context['object_list']
        self.assertTrue(app1 in object_list)
        self.assertTrue(app2 in object_list)
        self.assertTrue(app3 in object_list)

    def test_create_availability(self):
        # not logged in check
        tests.check_not_logged_in(self, "appointment:create_availability")

        # tutors only check
        user = UserFactory()
        self.client.force_login(user)
        tests.check_not_tutor(self, "appointment:create_availability")

        # actual tests

        self.client.logout()
        tutor = TutorFactory()
        self.client.force_login(tutor.user)
        # just make sure it has the form, test the form somewhere else
        # GET
        response = self.client.get(reverse("appointment:create_availability"))
        self.assertEqual(response.status_code, 200)
        form = response.context['availability_form']
        self.assertEqual(form, AvailabilityForm)

        # POST
        # dont test the form just make sure the view handles it properly
        data = {}
        response = self.client.post(reverse("appointment:create_availability"), data)
        form = response.context['availability_form']
        self.assertEqual(len(form.errors), 4)

        # tutor location
        data = {'date': '04/12/2020', 'start_time': '7:00am', 'end_time': '8:00am', 'location_choice': 'TUTOR_ADDRESS'}
        response = self.client.post(reverse("appointment:create_availability"), data)
        # check success message
        success_message = response.context['success_message']
        self.assertEqual(success_message, 'Appointment for 04/12/2020 07:00AM has been created!')
        # make sure appointment is saved
        appointment = Appointment.objects.filter(tutor=tutor)[0]
        self.assertIsNotNone(appointment)
        # given in UTC
        self.assertEqual(appointment.start_time.strftime(settings.DATE_FORMAT + ' ' + settings.TIME_FORMAT),
                         "04/12/2020 11:00AM")
        self.assertEqual(appointment.duration, 60)
        self.assertEqual(appointment.location, tutor.user.profile.address())
        self.assertEqual(appointment.tutor_comments, "")
        self.assertEqual(appointment.location_option, "TUTOR_ADDRESS")

        # user location
        data = {'date': '10/12/2022', 'start_time': '9:00am', 'end_time': '11:00am', 'location_choice': 'USER_ADDRESS'}
        response = self.client.post(reverse("appointment:create_availability"), data)
        # check success message
        success_message = response.context['success_message']
        self.assertEqual(success_message, 'Appointment for 10/12/2022 09:00AM has been created!')
        # make sure appointment is saved
        appointment = Appointment.objects.filter(tutor=tutor)[1]
        self.assertIsNotNone(appointment)
        # given in UTC
        self.assertEqual(appointment.start_time.strftime(settings.DATE_FORMAT + ' ' + settings.TIME_FORMAT),
                         "10/12/2022 01:00PM")
        self.assertEqual(appointment.duration, 120)
        self.assertEqual(appointment.location, 'United States')
        self.assertEqual(appointment.tutor_comments, "")
        self.assertEqual(appointment.location_option, "USER_ADDRESS")

        # other location
        data = {'date': '12/12/2021', 'start_time': '4:00pm', 'end_time': '4:30pm', 'location_choice': 'OTHER',
                'other_location': 'East Islip Public Library'}
        response = self.client.post(reverse("appointment:create_availability"), data)
        # check success message
        success_message = response.context['success_message']
        self.assertEqual(success_message, 'Appointment for 12/12/2021 04:00PM has been created!')
        # make sure appointment is saved
        appointment = Appointment.objects.filter(tutor=tutor)[2]
        self.assertIsNotNone(appointment)
        # given in UTC, dst gives 4 hour offset here
        self.assertEqual(appointment.start_time.strftime(settings.DATE_FORMAT + ' ' + settings.TIME_FORMAT),
                         "12/12/2021 09:00PM")
        self.assertEqual(appointment.duration, 30)
        self.assertEqual(appointment.location, 'East Islip Public Library')
        self.assertEqual(appointment.tutor_comments, "")
        self.assertEqual(appointment.location_option, "OTHER")

        # test overlap error message (not testing overlap here)
        data = {'date': '12/12/2021', 'start_time': '4:00pm', 'end_time': '4:30pm', 'location_choice': 'OTHER',
                'other_location': 'East Islip Public Library'}
        response = self.client.post(reverse("appointment:create_availability"), data)
        error_message = response.context['error_message']
        self.assertIsNotNone(error_message)
        self.assertEqual(error_message,
                         "Appointment for 12/12/2021 at 04:00PM cannot be created. It overlaps with a previously created appointment.")

    def test_detail_view_get_templates(self):
        appointment = AppointmentFactory()

        # not logged in check
        tests.check_not_logged_in(self, "appointment:detail", args=str(appointment.pk))

        # user login
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(reverse("appointment:detail", args=str(appointment.pk)))
        self.assertTemplateUsed(response, "appointment/appointment_detail_user.html")

        # user and booked
        appointment.user = user
        appointment.status = "BOOKED"
        appointment.save()
        response = self.client.get(reverse("appointment:detail", args=str(appointment.pk)))
        self.assertTemplateUsed(response, "appointment/appointment_detail_user_booked.html")

        # tutor owner
        appointment = AppointmentFactory()
        tutor = TutorFactory()
        tutor.save()
        appointment.tutor = tutor
        appointment.save()
        self.client.logout()
        self.client.force_login(tutor.user)
        response = self.client.get(reverse("appointment:detail", args=str(appointment.pk)))
        self.assertTemplateUsed(response, "appointment/appointment_detail_tutor.html")

    def test_detail_view_post(self):
        appointment = AppointmentFactory()

        # not logged in check
        tests.check_not_logged_in(self, "appointment:detail", args=str(appointment.pk))

        # user login
        user = UserFactory()
        self.client.force_login(user)

        # if its in one of these states just use the regular template to show the status
        appointment.status = "CANCELED"
        appointment.save()
        response = self.client.post(reverse("appointment:detail", args=str(appointment.pk)))
        self.assertTemplateUsed(response, "appointment/appointment_detail_user.html")

        appointment.status = "EXPIRED"
        appointment.save()
        response = self.client.post(reverse("appointment:detail", args=str(appointment.pk)))
        self.assertTemplateUsed(response, "appointment/appointment_detail_user.html")

        appointment.status = "COMPLETED"
        appointment.save()
        response = self.client.post(reverse("appointment:detail", args=str(appointment.pk)))
        self.assertTemplateUsed(response, "appointment/appointment_detail_user.html")

        # even if they are the user of the appointment dont give out much info in the tempalte
        appointment.user = user
        appointment.save()

        appointment.status = "CANCELED"
        appointment.save()
        response = self.client.post(reverse("appointment:detail", args=str(appointment.pk)))
        self.assertTemplateUsed(response, "appointment/appointment_detail_user.html")

        appointment.status = "EXPIRED"
        appointment.save()
        response = self.client.post(reverse("appointment:detail", args=str(appointment.pk)))
        self.assertTemplateUsed(response, "appointment/appointment_detail_user.html")

        appointment.status = "COMPLETED"
        appointment.save()
        response = self.client.post(reverse("appointment:detail", args=str(appointment.pk)))
        self.assertTemplateUsed(response, "appointment/appointment_detail_user.html")

        # tutor POSTing their own appointment
        # don't need to test all the combinations of statues and their invariants since that isnt being tested here
        self.client.logout()
        tutor = TutorFactory(user=user)
        appointment = AppointmentFactory(tutor=tutor, user=UserFactory(), status="REQUESTED")
        self.client.force_login(user)
        response = self.client.post(reverse("appointment:detail", args=str(appointment.pk)), {'accept': True})
        self.assertTemplateUsed(response, "appointment/appointment_detail_tutor.html")
        success_message = response.context['success_message']
        self.assertEqual(success_message, "The appointment request has been accepted!")

        appointment = AppointmentFactory(tutor=tutor, user=UserFactory(), status="REQUESTED")
        response = self.client.post(reverse("appointment:detail", args=str(appointment.pk)), {'decline': True})
        self.assertTemplateUsed(response, "appointment/appointment_detail_tutor.html")
        success_message = response.context['success_message']
        self.assertEqual(success_message, "The appointment request has been declined.")

        # status doesnt really matter here
        appointment = AppointmentFactory(tutor=tutor, user=UserFactory(), status="BOOKED")
        response = self.client.post(reverse("appointment:detail", args=str(appointment.pk)), {'cancel': True})
        self.assertTemplateUsed(response, "appointment/appointment_detail_tutor.html")
        success_message = response.context['success_message']
        self.assertEqual(success_message, "The appointment has been cancelled.")

        # user POSTing an appointment
        # user requesting
        self.client.logout()
        user = UserFactory()
        self.client.force_login(user)
        appointment = AppointmentFactory()
        response = self.client.post(reverse("appointment:detail", args=str(appointment.pk)),
                                    {'request': True, 'user_comments': 'pls give me appointment. ty'})
        appointment = Appointment.objects.get(pk=appointment.pk)
        self.assertEqual(appointment.user_comments, "pls give me appointment. ty")
        success_message = response.context['success_message']
        self.assertEqual(success_message, "The appointment has been requested!")
        self.assertTemplateUsed(response, "appointment/appointment_detail_user.html")

        # user cancelling
        appointment = AppointmentFactory(user=user, status='BOOKED')
        response = self.client.post(reverse("appointment:detail", args=str(appointment.pk)), {'cancel': True})
        success_message = response.context['success_message']
        self.assertEqual(success_message, "The appointment request has been cancelled.")
        self.assertTemplateUsed(response, "appointment/appointment_detail_user.html")

