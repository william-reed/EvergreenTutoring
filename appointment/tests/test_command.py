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
from .appointment_factory import AppointmentFactory
from profile.tests.user_factory import UserFactory
from django.core.management import call_command
from factory import Faker
import pytz
from appointment.models import Appointment


class CommandTests(TestCase):
    def setUp(self):
        AppointmentFactory(
            start_time=Faker('past_datetime', start_date="-30d", tzinfo=pytz.timezone('UTC')), status='OPEN')
        AppointmentFactory(
            start_time=Faker('past_datetime', start_date="-30d", tzinfo=pytz.timezone('UTC')), status='REQUESTED',
            user=UserFactory())
        AppointmentFactory(
            start_time=Faker('past_datetime', start_date="-30d", tzinfo=pytz.timezone('UTC')), status='BOOKED')
        AppointmentFactory(
            start_time=Faker('past_datetime', start_date="-30d", tzinfo=pytz.timezone('UTC')), status='COMPLETED')
        AppointmentFactory(
            start_time=Faker('past_datetime', start_date="-30d", tzinfo=pytz.timezone('UTC')), status='CANCELED')
        AppointmentFactory(
            start_time=Faker('past_datetime', start_date="-30d", tzinfo=pytz.timezone('UTC')), status='EXPIRED')

        AppointmentFactory(status="OPEN")
        AppointmentFactory(status="REQUESTED")
        AppointmentFactory(status="BOOKED")
        AppointmentFactory(status="COMPLETED")
        AppointmentFactory(status="CANCELED")
        AppointmentFactory(status="EXPIRED")


    def test_update_status(self):
        call_command('update_status')

        self.assertEqual(Appointment.objects.get(pk=1).status, 'EXPIRED')
        self.assertEqual(Appointment.objects.get(pk=2).status, 'EXPIRED')
        self.assertEqual(Appointment.objects.get(pk=3).status, 'COMPLETED')
        self.assertEqual(Appointment.objects.get(pk=4).status, 'COMPLETED')
        self.assertEqual(Appointment.objects.get(pk=5).status, 'CANCELED')
        self.assertEqual(Appointment.objects.get(pk=6).status, 'EXPIRED')

        self.assertEqual(Appointment.objects.get(pk=7).status, 'OPEN')
        self.assertEqual(Appointment.objects.get(pk=8).status, 'REQUESTED')
        self.assertEqual(Appointment.objects.get(pk=9).status, 'BOOKED')
        self.assertEqual(Appointment.objects.get(pk=10).status, 'COMPLETED')
        self.assertEqual(Appointment.objects.get(pk=11).status, 'CANCELED')
        self.assertEqual(Appointment.objects.get(pk=12).status, 'EXPIRED')
