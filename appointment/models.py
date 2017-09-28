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

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from tutor.models import Tutor
import datetime
from pytz import timezone
from evergreen import settings


# Appointment Model
class Appointment(models.Model):
    # The tutor
    ## Can be null to allow for deletion of their account and keeping the information of this appointment
    tutor = models.ForeignKey(Tutor, null=True, on_delete=models.SET_NULL)
    # The User
    ## same deletion status
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    # start time and date
    start_time = models.DateTimeField()
    # duration in minutes. maximum is 180 minutes.
    MAX_APPOINTMENT_DURATION_MINS = 180
    duration = models.PositiveIntegerField(validators=[MaxValueValidator(MAX_APPOINTMENT_DURATION_MINS)])
    # location TODO: maybe a location / address model field would be useful
    # can be null if the tutor wishes to use the users house
    location = models.CharField(max_length=80, null=True)
    # give the tutor the option to pick where they are available to tutor for this session
    LOCATION_CHOICES = [('TUTOR_ADDRESS', "Tutor's address"),
                        ('USER_ADDRESS', "User's address"),
                        ('OTHER', "Other")]
    location_option = models.CharField(max_length=10, choices=LOCATION_CHOICES)
    # status
    STATUS_CHOICES = [('OPEN', 'Open'),
                      ('REQUESTED', 'Requested'),
                      ('BOOKED', 'Booked'),
                      ('COMPLETED', 'Completed'),
                      ('CANCELED', 'Canceled'),
                      ('EXPIRED', 'Expired')]
    # does not actually create an ENUM in the database. TODO: if i care about this make a custom model.
    # I probably will care about this to ensure the invariant. And I cannot ensure it once I make an API so gotta
    # do this at some point
    # UPDATE:
    # Not all databases even support ENUM's so not sure where I stand on this one...
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')

    COMMENTS_MAX_LENGTH = 500
    # Tutor Comments
    tutor_comments = models.CharField(default="No tutor comments.", max_length=COMMENTS_MAX_LENGTH)
    # User Comments
    user_comments = models.CharField(default="No user comments.", max_length=COMMENTS_MAX_LENGTH)

    def __str__(self):
        """
        :return: the string of this object as: William Reed's appointment at 05-03-2016 4:00:00 for 30 minutes
        """
        return self.tutor.user.profile.name() + "'s appointment at " + self.start_time.strftime(
            settings.DATE_FORMAT + ' ' + settings.TIME_FORMAT) + ' (UTC) for ' + str(self.duration) + ' minutes'

    def end_time(self):
        """
        :return: the ending time of this appointment
        """
        return self.start_time + datetime.timedelta(minutes=self.duration)

    def cost(self):
        """
        :return: the cost of this appointment based off the tutors rate
        """
        return self.tutor.rate / 60 * self.duration

    def overlap(self, other):
        """
        does self overlap with other?
        :param other: another appointment
        :return: boolean
        """
        if self.start_time.year == other.start_time.year and self.start_time.month == other.start_time.month \
                and self.start_time.day == other.start_time.day and self.status != "CANCELED":

            duration = other.duration
            # check if the duration of start_time overlaps with the self.start_time
            if self.start_time > other.start_time:
                delta = self.start_time - other.start_time
                if delta.seconds / 60 < duration:
                    return True
            # check reverse
            else:
                delta = other.start_time - self.start_time
                if delta.seconds / 60 < self.duration:
                    return True

        return False

    # IMPORTANT:
    # the following are various methods to alter the status to ensure invariants of the model.
    # status is not meant to be directly altered.

    def request(self, user):
        """
        Request this appointment
        :param user: the user
        :return: None
        """
        if self.status != 'OPEN':
            raise ValueError('Appointment status must be "OPEN" in order to request it.')

        self.status = 'REQUESTED'
        self.user = user

        if self.location_option == "USER_ADDRESS":
            self.location = self.user.profile.address()

        # where is this num error coming from?
        self.tutor.user.profile.recieve_notification("Requested Appointment",
                                                     insert_date_link(self,
                                                                      self.user.profile.name()
                                                                      + ' has requested your {link} for {date}',
                                                                      self.tutor.user.profile.timezone))
        self.save()

    def cancel_tutor(self):
        """
        Cancel this appointment, notify users if there is one.
        :return: None
        """
        if self.status == 'COMPLETED' or self.status == 'CANCELED' or self.status == 'EXPIRED':
            raise ValueError('Appointment status must not be "COMPLETED" or "CANCELED" or "EXPIRED" to cancel it')

        self.status = "CANCELED"
        self.save()

        # notify user if there is one
        if self.user:
            self.user.profile.recieve_notification("Cancelled Appointment",
                                                   insert_date_link(self,
                                                                    self.tutor.user.profile.name()
                                                                    + ' has cancelled your {link} for {date}',
                                                                    self.user.profile.timezone))

    def cancel_user(self):
        """
        cancelation from the user of the appointment, notify the tutor
        :return: None
        """
        if self.status != 'BOOKED':
            raise ValueError('Appointment status must be "BOOKED" in order to cancel it by the user.')

        self.status = "OPEN"

        # notify the tutor
        self.tutor.user.profile.recieve_notification("Cancelled Appointment",
                                                     insert_date_link(self,
                                                                      self.user.profile.name()
                                                                      + ' has cancelled their request for {link} on {date}',
                                                                      self.tutor.user.profile.timezone))

        self.user = None
        self.user_comments = "No user comments."

        if self.location_option == "USER_ADDRESS":
            self.location = "United States"

        self.save()

    def accept(self):
        """
        Accept the user for this appointment
        :return: None
        """
        if self.status != "REQUESTED":
            raise ValueError('Appointment status must be "REQUESTED" in order to acceot it.')

        self.status = "BOOKED"
        self.save()

        self.user.profile.recieve_notification("Accepted Appointment",
                                               insert_date_link(self,
                                                                self.tutor.user.profile.name()
                                                                + ' has accepted the {link} request for {date} !',
                                                                self.user.profile.timezone))

    def decline(self):
        """
        Decline the user for this appointment, and eliminate the user reference
        :return: None
        """
        if self.status != "REQUESTED":
            raise ValueError('Appointment status must be "REQUESTED" in order to decline it.')
        else:
            self.status = "OPEN"
            self.user.profile.recieve_notification("Declined Appointment",
                                                   insert_date_link(self,
                                                                    self.tutor.user.profile.name() +
                                                                    ' has declined the {link} request for {date}',
                                                                    self.user.profile.timezone))
            self.user = None
            self.user_comments = "No user comments."
            if self.location_option == "USER_ADDRESS":
                self.location = "United States"
            self.save()

    def expire(self):
        """
        Call on expiration of this appointment
        :return: None
        """
        if self.end_time() > timezone('UTC').localize(datetime.datetime.now()):
            raise ValueError('You cannot expire an appointment that has not ended yet.')
        else:
            if self.status == 'BOOKED' or self.status == 'COMPLETED' or self.status == 'CANCELED' \
                    or self.status == 'EXPIRED':
                raise ValueError('The appointment must be OPEN or REQUESTED in order for it to expire.')
            elif self.status == "REQUESTED":
                self.user.profile.recieve_notification("Expired Appointment",
                                                       insert_date_link(self,
                                                                        "The {link} that you requested has expired.",
                                                                        self.user.profile.timezone))
            self.status = "EXPIRED"
            self.save()

    def complete(self):
        """
        Complete this appointment
        :return: None
        """
        if self.end_time() > timezone('UTC').localize(datetime.datetime.now()):
            raise ValueError('You cannot complete an appointment that has not ended yet.')
        else:
            if self.status != 'BOOKED':
                raise ValueError('The appointment needs to be BOOKED in order for it to be completed.')
            else:
                self.status = "COMPLETED"
                self.save()


def insert_date_link(app, message, tz):
    """
    Insert the appointment date and link into the given string.
    {date} = date
    {link} = link
    :param app: appointment object
    :param message: message to be altered
    :param tz: timezone string to use for the date
    :return: the html within the message - now marked as safe for use in templates
    """
    return message.replace('{date}', app.start_time.astimezone(timezone(tz))
                           .strftime("%m-%d-%Y %I:%M %p")) \
        .replace('{link}', '<a href="/appointment/' + str(app.pk) + '/"> appointment</a>')
