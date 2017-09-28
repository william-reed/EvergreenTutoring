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

from django.core.management.base import BaseCommand
from appointment.models import Appointment
import pytz
from datetime import datetime
from django.db.models import Q


class Command(BaseCommand):
    """
    Check if appointment statuses need to be changed based off of completion
    or their expiration
    """

    def handle(self, *args, **options):
        appointments = Appointment.objects.exclude(Q(status='COMPLETED') | Q(status='EXPIRED') | Q(status='CANCELED'))
        # logger = logging.getLogger('evergreen.cron')
        for app in appointments:
            if app.end_time() < pytz.timezone('UTC').localize(datetime.now()):
                if app.status == "BOOKED":
                    app.complete()
                elif app.status == "OPEN" or app.status == "REQUESTED":
                    app.expire()
                else:
                    pass
                    # logger.warning('Appointment with pk: ' + app.pk
                    #    + ' should be completed but it is in an illegal state!')
                    # logger.info('All appointment statuses have been updated.')
        self.stdout.write(self.style.SUCCESS('Successfully updated all appointment statuses'))
