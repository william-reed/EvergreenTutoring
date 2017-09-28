from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

app_name = 'profile'

urlpatterns = [
    # index for this app
    # /profile/
    url(r'^$', views.index, name='index'),
    # /profile/login/
    url(r'^login/$', auth_views.LoginView.as_view(template_name='profile/login.html', redirect_field_name=''),
        name="login"),
    # /profile/register/
    url(r'^register/$', views.register, name='register'),
    # /profile/logout/
    url(r'^logout/$', views.logout, name='logout'),
    # /profile/edit/
    url(r'^edit/$', views.edit, name='edit'),
]
