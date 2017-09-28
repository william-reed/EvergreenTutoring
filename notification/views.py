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

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


# Create your views here.

@login_required
def index(request):
    notifications = request.user.profile.notifications()
    # my hacky way to change the read reciept status after sending out the data
    try:
        return render(request, 'notification/notification_list.html', {'object_list': notifications})
    finally:
        # TODO: clean this up
        for notif_tuple in notifications:
            if not notif_tuple[0].read_by_user:
                notif_tuple[0].read_by_user = True
                notif_tuple[0].save()


@staff_member_required(login_url='/profile/login/')
def create_notification(request):
    if request.method == 'POST':
        channel = request.POST['channel']
        author = request.POST['author']
        subject = request.POST['subject']
        message = request.POST['message']
        user = request.user

        user.profile.send_notification(channel, author, subject, message)

        return render(request, 'notification/send_notification.html',
                      {'success_message': 'Notification successfully sent!'})
    else:
        return render(request, 'notification/send_notification.html')
