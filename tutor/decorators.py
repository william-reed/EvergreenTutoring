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

from django.http import HttpResponseRedirect


def tutors_only(function):
    """
    Decorator to only allow a tutor to access a page.
    Thanks for the help SO: https://stackoverflow.com/questions/5469159/how-to-write-a-custom-decorator-in-django
    :param function: succeeding function
    :return: honestly don't have a clue.
    """

    def wrap(request, *args, **kwargs):

        profile = request.user.profile
        if profile.is_tutor():
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
