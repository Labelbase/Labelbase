from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from two_factor.urls import urlpatterns as tf_urls

from .views import (
    ExampleSecretView, LabelbaseView, HomeView, RegistrationCompleteView, RegistrationView,
)

from userprofile.views import ProfileView

urlpatterns = [
    path(
        '',
        HomeView.as_view(),
        name='home',
    ),

    path(
        '',
        ProfileView.as_view(),
        name='profile',
    ),

    path(
        'labelbase/<int:labelbase_id>/',
        LabelbaseView.as_view(),
        name='labelbase',
    ),

    path(
        'account/logout/',
        LogoutView.as_view(),
        name='logout',
    ),
    path(
        'secret/',
        ExampleSecretView.as_view(),
        name='secret',
    ),
    path(
        'account/register/',
        RegistrationView.as_view(),
        name='registration',
    ),
    path(
        'account/register/done/',
        RegistrationCompleteView.as_view(),
        name='registration_complete',
    ),
    path('', include(tf_urls)),
    path('', include('user_sessions.urls', 'user_sessions')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
