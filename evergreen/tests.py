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

from django.urls import reverse


# generic helper tests to be used in various apps

def check_not_logged_in(test, view_name, **kwargs):
    """
    Call a view to confirm it has login_required. Expects no user to be logged in.
    :param test: the testing class (should be passed in as self)
    :param view_name: the name of a view with login_required
    :param kwargs: used to pass in args for detail view info or something
    :return: NoneType
    """
    if 'args' in kwargs:
        args = kwargs.pop('args')
        response = test.client.get(reverse(view_name, args=(args,)))
        test.assertRedirects(response, reverse("profile:login") + "?next=" + reverse(view_name, args=(args,)))
    else:
        response = test.client.get(reverse(view_name))
        test.assertRedirects(response, reverse("profile:login") + "?next=" + reverse(view_name))

    test.assertEqual(response.status_code, 302)


def check_not_tutor(test, view_name, **kwargs):
    """
    Call with your authenticated user to confirm that the method is only valid for tutors. Expects authenticated user
    to not be a tutor
    :param test:
    :param view_name: the name of a view with login_required
    :param kwargs: used to pass in args for detail view info or something
    :return: NoneType
    """
    if 'args' in kwargs:
        args = kwargs.pop('args')
        response = test.client.get(reverse(view_name, args=(args,)))
        test.assertRedirects(response, reverse("home"))
    else:
        response = test.client.get(reverse(view_name))
        test.assertRedirects(response, reverse("home"))
    test.assertEqual(response.status_code, 302)
