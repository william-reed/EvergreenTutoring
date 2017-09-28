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

from factory.django import DjangoModelFactory
from tutor.models import Tutor, Subject, Review
from profile.tests.user_factory import UserFactory
from factory import Faker, SubFactory


class TutorFactory(DjangoModelFactory):
    """
    Tutor Factory
    """

    class Meta:
        model = Tutor

    user = SubFactory(UserFactory)
    rate = Faker('random_number', digits=2)
    bio = Faker('sentence', nb_words=75)


class SubjectFactory(DjangoModelFactory):
    """
    Subject Factory
    """

    class Meta:
        model = Subject

    tutor = SubFactory(TutorFactory)
    name = Faker('word',
                 ext_word_list={'Trigonometry', 'Geometry', 'Calculus', 'World History', 'U.S. History', 'Economics',
                                'English', 'SAT', 'ACT', 'Chemistry', 'Biology'})


class ReviewFactory(DjangoModelFactory):
    """
    Review Factory
    """

    class meta:
        model = Review

    tutor = SubFactory(TutorFactory)
    user = SubFactory(UserFactory)
    anonymous = Faker('boolean')
    # TODO: how to get number in range?
    rating = 3
    text = Faker('sentence', nb_words=75)
