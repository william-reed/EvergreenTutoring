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
from appointment.models import Appointment
from factory import Faker, SubFactory
import pytz
from tutor.tests.tutor_factory import TutorFactory


class AppointmentFactory(DjangoModelFactory):
    """
    Defaults to building a tutor upon its initial state with no user, and a status of OPEN,
    in the next 30 days, at the tutors address
    """

    class Meta:
        model = Appointment

    tutor = SubFactory(TutorFactory)
    user = None
    start_time = Faker('future_datetime', end_date="+30d", tzinfo=pytz.timezone('UTC'))
    duration = Faker('random_number', digits=2)
    location = Faker('address')
    location_option = 'TUTOR_ADDRESS'
