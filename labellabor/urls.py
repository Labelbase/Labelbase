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
from .views import (
    LabelbaseView,
    LabelbaseDeleteView,
    LabelDeleteView,
    TermsView,
    HomeView,
    RegistrationCompleteView,
    LabelUpdateView,
    PrivacyView,
    RegistrationView,
    LabelbaseFormView,
    LabelbaseUpdateView,
    FaqView,
)
from importer.views import upload_labels
from exporter.views import stream_labels_as_jsonl
from django.contrib.auth import views as auth_views


urlpatterns = [
    # path('api/labelbase/<int:labelbase_id>/label/<int:id>/', api.label),
    path("api/v0/labelbase/", LabelbaseAPIView.as_view()),
    path("api/v0/labelbase/<int:id>/", LabelbaseAPIView.as_view()),
    path("api/v0/labelbase/<int:labelbase_id>/label/", LabelAPIView.as_view()),
    path("api/v0/labelbase/<int:labelbase_id>/label/<int:id>/", LabelAPIView.as_view()),
    path("api-reference/", include_docs_urls(title="Labelbase API")),
    path("account/apikey/", login_required(APIKeyView.as_view()), name="apikey"),
    path(
        "account/userprofile/",
        login_required(ProfileView.as_view()),
        name="userprofile",
    ),
    path(
        "labelbase/<pk>/delete/",
        login_required(LabelbaseDeleteView.as_view()),
        name="del_labelbase",
    ),
    path(
        "labelbase/<int:labelbase_id>/",
        login_required(LabelbaseView.as_view()),
        name="labelbase",
    ),
    path(
        "labelbase/<int:labelbase_id>/edit/",
        login_required(LabelbaseUpdateView.as_view()),
        name="edit_labelbase",
    ),
    path("labelbase/import/", upload_labels, name="import_labels"),
    path(
        "labelbase/export/<int:labelbase_id>/",
        stream_labels_as_jsonl,
        name="export_labels",
    ),
    path(
        "labelbase/", login_required(LabelbaseFormView.as_view()), name="labelbase_new"
    ),
    # path('labelbase/<int:labelbase_id>/label/<int:label_id>/edit/', login_required(LabelUpdateView.as_view()), name='edit_label'),
    path(
        "label/<int:pk>/edit/",
        login_required(LabelUpdateView.as_view()),
        name="edit_label",
    ),
    path(
        "label/<int:pk>/delete/",
        login_required(LabelDeleteView.as_view()),
        name="del_label",
    ),
    path("account/logout/", LogoutView.as_view(), name="logout"),
    path("account/register/", RegistrationView.as_view(), name="registration"),
    path(
        "account/register/done/",
        RegistrationCompleteView.as_view(),
        name="registration_complete",
    ),
    path(
        "account/change-password/",
        auth_views.PasswordChangeView.as_view(
            template_name="change_password.html", success_url="/"
        ),
        name="change_password",
    ),
    path("privacy-policy", PrivacyView.as_view(), name="privacy_policy"),
    path("terms", TermsView.as_view(), name="terms"),
    path("faq", FaqView.as_view(), name="faq"),
    path("", HomeView.as_view(), name="home"),
    path("", include(tf_urls)),
    path("", include("user_sessions.urls", "user_sessions")),
    path("admin/", admin.site.urls),
]
