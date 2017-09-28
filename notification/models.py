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


# Notification Model
## may be more appropriately named as a Message
class Notification(models.Model):
    # this user sent the message.
    ## If they delete their account keep the message
    from_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    # who has names longer than 30 chars?
    ## including so I can do things like: from Evergreen Staff
    author = models.CharField(max_length=30)
    # subject
    subject = models.CharField(max_length=50)
    # message
    message = models.CharField(max_length=500)
    # time / date
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject + ' from ' + self.author + ' on ' + str(self.time_stamp)


# keeps track of where the notification is going and if it was read
# useful to send out messages to multiple people without duplicating Notification data - only this data
class DeliveryInfo(models.Model):
    # the notification
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    # to this user
    ## if their account is deleted, delete the notification / message. no need for it
    to_user = models.ForeignKey(User, on_delete=models.CASCADE)
    # read status
    read_by_user = models.BooleanField(default=False)

    def __str__(self):
        if self.read_by_user:
            return self.notification.__str__() + ' read by ' + self.to_user.__str__()
        else:
            return self.notification.__str__() + ' unread by ' + self.to_user.__str__()
