from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from two_factor.urls import urlpatterns as tf_urls

from labelbase.api import LabelAPIView

from .views import (LabelbaseView, HomeView, RegistrationCompleteView,
    RegistrationView, LabelbaseFormView )
# ExampleSecretView,


from rest_framework.documentation import include_docs_urls

from userprofile.views import ProfileView, APIKeyView
"""
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    #path('api/v1/', api.labelbase),

]

urlpatterns = format_suffix_patterns(urlpatterns)

"""

urlpatterns = [
    #path('api/v0/labelbase/<int:labelbase_id>/label/<int:id>/', api.label),
    path('api/v0/labelbase/<int:labelbase_id>/label/<int:id>/',
        LabelAPIView.as_view(), name='api_label'),

    path('api-reference/', include_docs_urls(title='Labelbase API')),
    path('account/apikey/', APIKeyView.as_view(), name='apikey'),
    path('account/userprofile/', ProfileView.as_view(), name='userprofile'),

    path('labelbase/', LabelbaseFormView.as_view(), name='labelbase_new'),
    path('labelbase/<int:labelbase_id>/', LabelbaseView.as_view(), name='labelbase'),
    path('account/logout/', LogoutView.as_view(), name='logout'),
    path('account/register/',RegistrationView.as_view(), name='registration'),
    path('account/register/done/', RegistrationCompleteView.as_view(), name='registration_complete'),
    path('', HomeView.as_view(), name='home'),
    path('', include(tf_urls)),
    path('', include('user_sessions.urls', 'user_sessions')),
    path('admin/', admin.site.urls),
    #path(
    #    'secret/',
    #    ExampleSecretView.as_view(),
    #    name='secret',
    #),

]
