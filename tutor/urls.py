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

from django.conf.urls import url
from . import views

app_name = 'tutor'

urlpatterns = [

    # /tutor/
    # list view
    url(r'^$', views.IndexView.as_view(), name='index'),
    # /tutor/register/
    url(r'^register/$', views.register, name='register'),
    # /tutor/edit/
    url(r'^edit/$', views.edit, name='edit'),
    # /tutor/<id>/
    # detail view
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    # /tutor/<id>/review/
    # review a tutor
    url(r'^(?P<pk>[0-9]+)/review/$', views.review, name='review'),
]
