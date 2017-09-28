from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator
from notification.models import Notification, DeliveryInfo
from tutor.models import Tutor
import datetime, pytz
from appointment.models import Appointment


# A user profile - add ons to the default User
class Profile(models.Model):
    # the user to connect to, if deleted, delete this too
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # the address information
    street_address = models.CharField(max_length=40, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    state = models.CharField(max_length=20, null=True, blank=True)
    zip = models.PositiveIntegerField(validators=[MaxValueValidator(99999)], null=True, blank=True)
    # link to their profile picture
    picture = models.CharField(max_length=200, default="http://i.imgur.com/4XjtXzO.png")
    timezone = models.CharField(max_length=35, default="America/New_York")

    # TODO: what other additional info do we need here? phone # ?

    # Profile model will be automatically created/updated when we create/update User instances.
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    # get the full name of this Profile
    def name(self):
        return self.user.first_name + ' ' + self.user.last_name

    # William Reed - wreed58@gmail.com
    def __str__(self):
        return self.name() + ' - ' + self.user.email

    def address(self):
        """
        Get the full address of the user
        :return: the address of the user
        """
        return self.street_address + ' ' + self.city + ' ' + self.state + ' ' + str(self.zip)

    # [12:53] <mattmcc> wreed: Typically you'd follow the model relationship.
    # [12:53] <mattmcc> user.notification_set.all() or somesuch.
    # and thus we have these methods in this class:

    # TODO: how is this stuff sorted? need to make sure its reverse chronological
    def notifications(self):
        """
        :return: all of the notifications / messages for this user.
        Information is returned as a tuple of the DeliveryInfo and the Notification in that order
        """
        notifications_to_get = DeliveryInfo.objects.filter(to_user=self.user)
        notifications = []

        for del_info in notifications_to_get:
            notifications.append((del_info, del_info.notification))

        return notifications

    def unread_notification_count(self):
        """
        :return: the count of unread messages for this user
        """
        return DeliveryInfo.objects.filter(to_user=self.user).filter(read_by_user=False).count()

    # TODO: I should really pick up a python book. too much java stuck in my brain smh
    # and html / css too...

    # TODO: change all documentation to this style

    def send_notification(self, to_users, author, subject, message):
        """
        sends a notification
        :param to_users: list of users to send the notification to, or the channel as a string: ALL, TUTORS, STAFF
        :param author: the String name to display that wrote this
        :param subject: the subject of the notificaiton
        :param message: message body
        :return: None
        """
        # TODO: if no staff permission, exit
        # create the notification
        notification = Notification(from_user=self.user, author=author, subject=subject, message=message)
        notification.save()

        # create the delivery information based on the channel or lack of
        # can i abstract this at all? Subtle differences make it look tricky to pull off
        if to_users == "ALL":
            for user in User.objects.all():
                del_info = DeliveryInfo(notification=notification, to_user=user)
                del_info.save()
        elif to_users == "TUTORS":
            for tutor in Tutor.objects.all():
                del_info = DeliveryInfo(notification=notification, to_user=tutor.user)
                del_info.save()
        elif to_users == "STAFF":
            for user in User.objects.filter(is_staff=True):
                del_info = DeliveryInfo(notification=notification, to_user=user)
                del_info.save()
        elif isinstance(to_users, str):
            raise ValueError(
                "to_users is given a str value, yet it is not an appropriate channel."
                " Appropriate channels are ALL, TUTORS, or STAFF")
        else:
            for user in to_users:
                del_info = DeliveryInfo(notification=notification, to_user=user)
                del_info.save()

    def read_notification(self, notification):
        """
        :param notification: noti
        :return: true if the user has read this notification
        """
        return DeliveryInfo.objects.filter(to_user=self.user).get(notification=notification).read_by_user

    def recieve_notification(self, subject, message, author="Evergreen Team"):
        """
        Convenience method to give this user a notification
        :param subject: subject
        :param message: message
        :param author: author defaults to 'Evergreen Team'
        :return: None
        """

        # we are just going to set the from user to him/herself here
        notification = Notification(from_user=self.user, author=author, subject=subject, message=message)
        notification.save()
        del_info = DeliveryInfo(notification=notification, to_user=self.user)
        del_info.save()

    def is_tutor(self):
        """
        is this user a tutor?
        :return: The tutor if he exists, or False
        """
        try:
            return Tutor.objects.get(user=self.user)
        except Tutor.DoesNotExist:
            return False

    def all_appointments(self):
        """
        Return a users appointments. If its a tutor return their hosted appointments
        :return: all of the appointments that this user is the 'appointment user' of in reverse chronological order
        """
        if self.is_tutor():
            return Appointment.objects.filter(tutor=self.is_tutor()).order_by('-start_time')
        else:
            return Appointment.objects.filter(user=self.user).order_by('-start_time')
