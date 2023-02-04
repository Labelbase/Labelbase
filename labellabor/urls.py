from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from two_factor.urls import urlpatterns as tf_urls

from labelbase import api

from .views import (
    ExampleSecretView, LabelbaseView, HomeView, RegistrationCompleteView, RegistrationView
)
from django.views.generic import TemplateView
from userprofile.views import ProfileView
"""
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    #path('api/v1/', api.labelbase),

]

urlpatterns = format_suffix_patterns(urlpatterns)

"""
urlpatterns = [

    path('api/v1/labelbase/<int:labelbase_id>/label/<int:id>/', api.label),

    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
    #    extra_context={'schema_url':'openapi-schema'}
    ), name='swagger-ui'),


    path(
        '',
        HomeView.as_view(),
        name='home',
    ),

    path(
        'account/userprofile/',
        ProfileView.as_view(),
        name='userprofile',
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
