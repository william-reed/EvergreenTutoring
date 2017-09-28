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
import appointment.models
import datetime
from .appointment_factory import AppointmentFactory
from profile.tests.user_factory import UserFactory
import pytz
from evergreen import settings


class AppointmentModelTests(TestCase):
    # make sure appointment overlap is ok
    def test_overlap(self):
        app1 = AppointmentFactory(start_time=datetime.datetime.now(tz=pytz.timezone('UTC')), duration=60)
        app2 = AppointmentFactory(
            start_time=datetime.datetime.now(tz=pytz.timezone('UTC')) + datetime.timedelta(minutes=60), duration=60)
        app3 = AppointmentFactory(
            start_time=datetime.datetime.now(tz=pytz.timezone('UTC')) + datetime.timedelta(minutes=59), duration=60)
        app4 = AppointmentFactory(
            start_time=datetime.datetime.now(tz=pytz.timezone('UTC')) + datetime.timedelta(minutes=61), duration=60)
        app5 = AppointmentFactory(
            start_time=datetime.datetime.now(tz=pytz.timezone('UTC')) + datetime.timedelta(days=365), duration=60)

        self.assertFalse(app1.overlap(app2))
        self.assertFalse(app2.overlap(app1))

        self.assertFalse(app1.overlap(app5))
        self.assertFalse(app5.overlap(app1))

        self.assertTrue(app1.overlap(app3))
        self.assertTrue(app3.overlap(app1))

        self.assertFalse(app1.overlap(app4))
        self.assertFalse(app4.overlap(app1))

        self.assertTrue(app2.overlap(app3))
        self.assertTrue(app3.overlap(app2))

        self.assertTrue(app5.overlap(app5))

    def setUp(self):
        self.user = UserFactory()
        self.app = AppointmentFactory.create()
        self.tutor = self.app.tutor

    def test_request(self):
        self.app.request(self.user)
        self.assertEqual(self.app.status, 'REQUESTED')
        self.assertIs(self.app.user, self.user)
        # implies they got a message from the request
        self.assertIs(self.tutor.user.profile.unread_notification_count(), 1)

        self.setUp()
        self.app.location_option = "USER_ADDRESS"
        self.app.request(self.user)
        self.assertEqual(self.app.location, self.user.profile.address())

        self.setUp()
        self.app.status = 'COMPLETED'
        self.assertRaises(ValueError, self.app.request, self.user)
        self.app.status = 'EXPIRED'
        self.assertRaises(ValueError, self.app.request, self.user)
        self.app.status = 'CANCELED'
        self.assertRaises(ValueError, self.app.request, self.user)
        self.app.status = 'BOOKED'
        self.assertRaises(ValueError, self.app.request, self.user)
        self.app.status = 'REQUESTED'
        self.assertRaises(ValueError, self.app.request, self.user)

    def test_cancel_tutor(self):
        self.app.cancel_tutor()
        self.assertIs(self.app.status, 'CANCELED')

        self.setUp()
        self.app.status = 'BOOKED'
        self.app.user = self.user
        self.app.cancel_tutor()
        self.assertEqual(self.app.status, 'CANCELED')
        self.assertIs(self.user.profile.unread_notification_count(), 1)

        self.setUp()
        self.app.status = 'COMPLETED'
        self.assertRaises(ValueError, self.app.cancel_tutor)
        self.app.status = 'EXPIRED'
        self.assertRaises(ValueError, self.app.cancel_tutor)
        self.app.status = 'CANCELED'
        self.assertRaises(ValueError, self.app.cancel_tutor)

    def test_cancel_user(self):
        self.app.status = 'BOOKED'
        self.app.user = self.user

        self.app.cancel_user()
        self.assertIs(self.tutor.user.profile.unread_notification_count(), 1)
        self.assertIsNone(self.app.user)
        self.assertEqual(self.app.user_comments, "No user comments.")

        self.setUp()
        self.app.status = 'BOOKED'
        self.app.user = self.user
        self.app.location_option = 'USER_ADDRESS'
        self.app.location = "Poop Town USA"
        self.app.cancel_user()
        self.assertEqual(self.app.location, 'United States')

        self.setUp()
        self.app.status = 'COMPLETED'
        self.assertRaises(ValueError, self.app.cancel_user)
        self.app.status = 'EXPIRED'
        self.assertRaises(ValueError, self.app.cancel_user)
        self.app.status = 'CANCELED'
        self.assertRaises(ValueError, self.app.cancel_user)
        self.app.status = 'OPEN'
        self.assertRaises(ValueError, self.app.cancel_user)
        self.app.status = 'REQUESTED'
        self.assertRaises(ValueError, self.app.cancel_user)

    def test_accept(self):
        self.app.status = 'REQUESTED'
        self.app.user = self.user
        self.app.accept()

        self.assertEqual(self.app.status, 'BOOKED')
        self.assertIs(self.user.profile.unread_notification_count(), 1)

        self.setUp()
        self.app.status = 'COMPLETED'
        self.assertRaises(ValueError, self.app.accept)
        self.app.status = 'EXPIRED'
        self.assertRaises(ValueError, self.app.accept)
        self.app.status = 'CANCELED'
        self.assertRaises(ValueError, self.app.accept)
        self.app.status = 'OPEN'
        self.assertRaises(ValueError, self.app.accept)
        self.app.status = 'BOOKED'
        self.assertRaises(ValueError, self.app.accept)

    def test_decline(self):
        self.app.status = 'REQUESTED'
        self.app.user = self.user
        self.app.decline()

        self.assertEqual(self.app.user_comments, 'No user comments.')
        self.assertIsNone(self.app.user)
        self.assertIs(self.user.profile.unread_notification_count(), 1)

        self.setUp()
        self.app.user = self.user
        self.app.location_option = "USER_ADDRESS"
        self.app.location = "Poop Town USA"
        self.app.status = 'REQUESTED'
        self.app.decline()
        self.assertEqual(self.app.location, 'United States')

        self.setUp()
        self.app.status = 'COMPLETED'
        self.assertRaises(ValueError, self.app.decline)
        self.app.status = 'EXPIRED'
        self.assertRaises(ValueError, self.app.decline)
        self.app.status = 'CANCELED'
        self.assertRaises(ValueError, self.app.decline)
        self.app.status = 'OPEN'
        self.assertRaises(ValueError, self.app.decline)
        self.app.status = 'BOOKED'
        self.assertRaises(ValueError, self.app.decline)

    def test_expire(self):
        self.assertRaises(ValueError, self.app.expire)

        self.setUp()
        self.app.status = 'REQUESTED'
        self.app.user = self.user
        self.app.start_time = pytz.timezone('UTC').localize(datetime.datetime.now() - datetime.timedelta(days=10))
        self.app.expire()
        self.assertIs(self.user.profile.unread_notification_count(), 1)
        self.assertEqual(self.app.status, "EXPIRED")

        self.setUp()
        self.app.start_time = pytz.timezone('UTC').localize(datetime.datetime.now() - datetime.timedelta(days=10))
        self.app.status = 'BOOKED'
        self.assertRaises(ValueError, self.app.expire)
        self.app.status = 'COMPLETED'
        self.assertRaises(ValueError, self.app.expire)
        self.app.status = 'CANCELED'
        self.assertRaises(ValueError, self.app.expire)
        self.app.status = 'EXPIRED'
        self.assertRaises(ValueError, self.app.expire)

    def test_complete(self):
        self.assertRaises(ValueError, self.app.complete)

        self.setUp()
        self.app.status = 'BOOKED'
        self.app.start_time = pytz.timezone('UTC').localize(datetime.datetime.now() - datetime.timedelta(days=10))
        self.app.complete()
        self.assertEqual(self.app.status, "COMPLETED")

        self.setUp()
        self.app.start_time = pytz.timezone('UTC').localize(datetime.datetime.now() - datetime.timedelta(days=10))
        self.app.status = 'COMPLETED'
        self.assertRaises(ValueError, self.app.complete)
        self.app.status = 'EXPIRED'
        self.assertRaises(ValueError, self.app.complete)
        self.app.status = 'CANCELED'
        self.assertRaises(ValueError, self.app.complete)
        self.app.status = 'OPEN'
        self.assertRaises(ValueError, self.app.complete)
        self.app.status = 'REQUESTED'
        self.assertRaises(ValueError, self.app.complete)

    def test_insert_date_link(self):
        message = appointment.models.insert_date_link(self.app, 'hello', 'UTC')
        self.assertEqual(message, 'hello')

        self.setUp()
        message = appointment.models.insert_date_link(self.app, '{date}', 'UTC')
        self.assertEqual(message, self.app.start_time.strftime("%m-%d-%Y %I:%M %p"))

        self.setUp()
        message = appointment.models.insert_date_link(self.app, 'the appointment date is: {date} - see you there',
                                                      'UTC')
        self.assertEqual(message, 'the appointment date is: ' + self.app.start_time.strftime(
            "%m-%d-%Y %I:%M %p") + ' - see you there')

        self.setUp()
        message = appointment.models.insert_date_link(self.app, '{link}', 'UTC')
        self.assertEqual(message, '<a href="/appointment/' + str(self.app.pk) + '/"> appointment</a>')

        self.setUp()
        message = appointment.models.insert_date_link(self.app, 'here is the link to the {link} click it now', 'UTC')
        self.assertEqual(message, 'here is the link to the <a href="/appointment/' + str(
            self.app.pk) + '/"> appointment</a> click it now')

        self.setUp()
        message = appointment.models \
            .insert_date_link(self.app, 'A user has just requested your {link} to your appointment on {date}', 'UTC')
        self.assertEqual(message, 'A user has just requested your <a href="/appointment/' + str(
            self.app.pk) + '/"> appointment</a> to your appointment on ' + self.app.start_time.strftime(
            "%m-%d-%Y %I:%M %p"))

    def test_str(self):
        start_time = "04/13/2017 05:00AM"
        duration = 60
        appointment = AppointmentFactory(start_time=pytz.utc.localize(
            datetime.datetime.strptime(start_time, settings.DATE_FORMAT + ' ' + settings.TIME_FORMAT)),
            duration=duration)

        self.assertEqual(appointment.__str__(),
                         appointment.tutor.user.profile.name() + "'s appointment at " + start_time + " (UTC) for " + str(
                             duration) + " minutes")

        start_time = "12/02/2003 12:30PM"
        duration = 120
        appointment = AppointmentFactory(
            start_time=pytz.utc.localize(
                datetime.datetime.strptime(start_time, settings.DATE_FORMAT + ' ' + settings.TIME_FORMAT)),
            duration=duration)
        self.assertEqual(appointment.__str__(),
                         appointment.tutor.user.profile.name() + "'s appointment at " + start_time + " (UTC) for " + str(
                             duration) + " minutes")
