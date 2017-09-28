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

from django.views import generic
from .models import Tutor, Subject, Review
from appointment.models import Appointment
from django.contrib.auth.decorators import login_required
from .forms import TutorForm, SubjectForm, ReviewForm
from django.shortcuts import render, redirect
from django.forms.formsets import formset_factory
from .decorators import tutors_only
from django.shortcuts import get_object_or_404


class IndexView(generic.ListView):
    """
    Tutor index view
    """
    template_name = 'tutor/tutor_list.html'

    def get_queryset(self):
        return Tutor.objects.all()


class DetailView(generic.DetailView):
    """
    Tutor detail view
    """
    model = Tutor
    template_name = 'tutor/tutor_detail.html'


# Write a review for a tutor
def write_review(request):
    pass


def view_all_tutor_reviews(request):
    pass


@login_required
def register(request):
    tutor = request.user.profile.is_tutor()
    if tutor:
        return redirect('tutor:index')

    # create the formset
    SubjectFormSet = formset_factory(SubjectForm)

    if request.method == "POST":
        tutor_form = TutorForm(request.POST)
        if tutor_form.is_valid():
            tutor = tutor_form.save(commit=False)
            tutor.user = request.user
            tutor.save()

            subject_formset = SubjectFormSet(request.POST)
            if subject_formset.is_valid():
                for subject_form in subject_formset:
                    subject = Subject(tutor=tutor, name=subject_form.cleaned_data.get('name'))
                    subject.save()
                # success at this point
                return redirect('/tutor/' + str(tutor.pk) + '/')
        return render(request, 'tutor/tutor.html',
                      {'tutor_form': tutor_form, 'subject_formset': SubjectFormSet(request.POST),
                       'name': 'Tutor Registration'})
    else:
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '1', }

        tutor_form = TutorForm
        subject_formset = SubjectFormSet(data)
        return render(request, 'tutor/tutor.html',
                      {'tutor_form': tutor_form, 'subject_formset': subject_formset, 'name': 'Tutor Registration'})


@login_required
@tutors_only
def edit(request):
    # create the formset
    SubjectFormSet = formset_factory(SubjectForm, extra=0, min_num=1)

    if request.method == "POST":
        tutor = request.user.profile.is_tutor()
        tutor_form = TutorForm(request.POST, instance=tutor)
        subject_formset = SubjectFormSet(request.POST)
        if tutor_form.is_valid() and subject_formset.is_valid():
            tutor_form.save()
            # TODO: whats the better way to do this rather than deleting them all and adding
            Subject.objects.filter(tutor=tutor).delete()
            for subject_form in subject_formset:
                subject = subject_form.save(commit=False)
                subject.tutor = tutor
                subject.save()

            return redirect('/tutor/' + str(tutor.pk) + '/')

    else:
        tutor = request.user.profile.is_tutor()
        # IDK WHAT THIS IS BUT I SAW IT ONLINE WOW
        subjects = [{'tutor': tutor, 'name': s}
                    for s in tutor.subjects()]

        tutor_form = TutorForm(instance=tutor)
        subject_formset = SubjectFormSet(initial=subjects)

    return render(request, 'tutor/tutor.html',
                  {'tutor_form': tutor_form, 'subject_formset': subject_formset, 'name': 'Edit your Tutor Profile'})


@login_required
def review(request, *args, **kwargs):
    """
    create or edit your review for a tutor
    """
    pk = kwargs.get('pk')
    # make sure tutor exists
    tutor = get_object_or_404(Tutor, pk=pk)
    user = request.user

    # make sure the user has a completed session with the tutor
    user_tutor_apps = Appointment.objects.filter(tutor=tutor, user=user, status='COMPLETED').count()
    if user_tutor_apps <= 0:
        # TODO: use messages to send an error message with it
        return redirect('tutor:detail', pk=pk)

    # editing a review or adding a new one?
    user_tutor_review = Review.objects.filter(tutor=tutor, user=user)

    # edit
    if user_tutor_review.count() > 0:
        if request.method == "POST":
            review_form = ReviewForm(request.POST, instance=user_tutor_review.first())
            review_form.save(tutor=tutor, user=user)
            # TODO: use messages to send a success message with it
            return redirect('tutor:detail', pk=pk)
        else:
            review_form = ReviewForm(instance=user_tutor_review.first())
    # add a new
    else:
        if request.method == "POST":
            review_form = ReviewForm(request.POST)
            review_form.save(tutor=tutor, user=user)
            # TODO: use messages to send a success message with it
            return redirect('tutor:detail', pk=pk)
        else:
            review_form = ReviewForm

    return render(request, 'tutor/review.html', {'review_form': review_form, 'tutor': tutor})