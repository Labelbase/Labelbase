from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from two_factor.urls import urlpatterns as tf_urls
from labelbase.api import LabelAPIView, LabelbaseAPIView
from rest_framework.documentation import include_docs_urls
from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.auth.decorators import login_required
from userprofile.views import ProfileView, APIKeyView
from .views import (LabelbaseView, LabelbaseDeleteView,
                    HomeView, RegistrationCompleteView,
                    RegistrationView, LabelbaseFormView )



urlpatterns = [
    #path('api/labelbase/<int:labelbase_id>/label/<int:id>/', api.label),
    path('api/v0/labelbase/', LabelbaseAPIView.as_view()),
    path('api/v0/labelbase/<pk>/', LabelbaseAPIView.as_view()),
    path('api/v0/labelbase/<pk>/label/', LabelAPIView.as_view()),
    path('api/v0/labelbase/<int:labelbase_id>/label/<int:id>/', LabelAPIView.as_view()),
    path('api-reference/', include_docs_urls(title='Labelbase API')),
    path('account/apikey/', login_required(APIKeyView.as_view()), name='apikey'),
    path('account/userprofile/', login_required(ProfileView.as_view()), name='userprofile'),
    path('labelbase/', login_required(LabelbaseFormView.as_view()), name='labelbase_new'),
    path('labelbase/<pk>/delete/', login_required(LabelbaseDeleteView.as_view()),  name='del_labelbase'),
    path('labelbase/<int:labelbase_id>/', login_required(LabelbaseView.as_view()), name='labelbase'),
    path('account/logout/', LogoutView.as_view(), name='logout'),
    path('account/register/', RegistrationView.as_view(), name='registration'),
    path('account/register/done/', RegistrationCompleteView.as_view(), name='registration_complete'),
    path('', HomeView.as_view(), name='home'),
    path('', include(tf_urls)),
    path('', include('user_sessions.urls', 'user_sessions')),
    path('admin/', admin.site.urls),


]
