from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import UserForm, ProfileForm, EditAccountForm
from django.shortcuts import render, redirect


@login_required
def index(request):
    """
    Profile page
    """
    return render(request, 'profile/profile.html', {'user': request.user})


def register(request):
    """
    Create an account
    """
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            # tried setting user.profile to the saved form but it was wacky. might have to do with profile creation
            # upon a user being created.
            user.profile.street_address = profile_form.cleaned_data['street_address']
            user.profile.city = profile_form.cleaned_data['city']
            user.profile.state = profile_form.cleaned_data['state']
            user.profile.zip = profile_form.cleaned_data['zip']

            # authenticate them
            auth_login(request, user)
            # success, redirect them to their profile
            # TODO: display successfully created account on redirect page
            return redirect('profile:index')
    else:
        user_form = UserForm()
        profile_form = ProfileForm()

    return render(request, 'profile/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
def logout(request):
    """
    Logout
    """
    auth_logout(request)
    # TODO: use messages to display success message after log out
    return redirect('profile:login')


@login_required
def edit(request):
    """
    Edit your profile
    """
    if request.method == 'POST':
        form = EditAccountForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = request.user
            profile = request.user.profile

            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.email = data.get('email')
            user.save()

            profile.street_address = data.get('street_address')
            profile.city = data.get('city')
            profile.state = data.get('state')
            profile.zip = data.get('zip')
            profile.save()

            # need to use message framework to send success message. do the same for logout
            # TODO: display success
            return redirect('profile:index')
        else:
            return render(request, 'profile/edit.html', {'errors', form.errors})
    else:
        # Can't really user forms the nice way since i am not representing the whole model
        edit_form = EditAccountForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'street_address': request.user.profile.street_address,
            'city': request.user.profile.city,
            'state': request.user.profile.state,
            'zip': request.user.profile.zip})
        return render(request, 'profile/edit.html', {'form': edit_form})
