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
# stupid workaround to stop problems with circular imports
# maybe another way or stop circular imports
import appointment
from django.core.validators import MaxValueValidator, MinValueValidator


# A tutor
class Tutor(models.Model):
    # connect this to a user. If the user is deleted, delete this tutor too
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # hourly rate for the tutor
    rate = models.DecimalField(decimal_places=2, max_digits=5)
    # 1500 characters is about 250 words. should be enough
    BIO_MAX_LENGTH = 1500
    bio = models.CharField(max_length=BIO_MAX_LENGTH)

    # link to personal site or something?

    # get the list of subjects (as strings) that this tutor covers
    def subjects(self):
        tutor_subjects = Subject.objects.filter(tutor=self)
        subject_strings = []

        for subject in tutor_subjects:
            subject_strings.append(subject.name)

        return subject_strings

    # William Reed
    def __str__(self):
        return self.user.profile.name()

    # get all the reviews for this tutor
    def reviews(self):
        return Review.objects.filter(tutor=self)

    # get the numerical rating for this tutor
    def rating(self):
        all_reviews = Review.objects.filter(tutor=self)
        sum = 0

        for review in all_reviews:
            sum += review.rating

        if sum == 0:
            return 0
        else:
            return sum / len(all_reviews)

    def sessions(self):
        """
        :return: the total number of sessions this tutor has completed
        """
        return appointment.models.Appointment.objects.filter(tutor=self, status='COMPLETED').count()

    # TODO: make sure this is ordered ok
    def appointments(self):
        """
        :return:  get the 'OPEN' appointments for this tutor
        """
        return appointment.models.Appointment.objects.filter(tutor=self, status='OPEN')


# subjects of a Tutor
class Subject(models.Model):
    # connect this to a Tutor. If the tutor / user is deleted, delete this too
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    # subject name
    name = models.CharField(max_length=30)

    # William Reed - Mathematics
    def __str__(self):
        return self.tutor.user.profile.name() + ' - ' + self.name


"""
5/14/17
i think this might deserve its own app. 
Neither user / tutor deserves it more
both will need access to write, view, edit reviews

5/15/17
going to try it here. it certainly is more nested in tutors than users so maybe this isnt a bad call.
"""


# A tutor review by a user
class Review(models.Model):
    # connect this to a Tutor. If the tutor / user is deleted, delete this too
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    # the user that wrote this
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # is this review supposed to be from an anonymous author? dont show author if true
    anonymous = models.BooleanField()
    # the rating of this tutor from 1-5
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    # 1500 characters is about 250 words. should be enough
    TEXT_MAX_LENGTH = 1500
    text = models.CharField(max_length=TEXT_MAX_LENGTH)
    # date of the review
    time_stamp = models.DateTimeField(auto_now_add=True)

    # TODO: add a check to make sure only one review per user/tutor combo

    # William Reed by John Francis: 3.3/5.0
    def __str__(self):
        return self.tutor.user.profile.name() + " by " + self.user.profile.name() + ": " + str(self.rating) + "/5"

    # get the appropriate amount of stars for this review
    # easier to do here than a template
    def stars(self):
        i = self.rating
        star_string = ""

        while i > 0:
            star_string += "★"
            i -= 1

        return star_string
