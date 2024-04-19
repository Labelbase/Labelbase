from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from two_factor.urls import urlpatterns as tf_urls
from labelbase.api import LabelAPIView, LabelbaseAPIView
from rest_framework.documentation import include_docs_urls
from django.contrib.auth.decorators import login_required

from userprofile.views import (ProfileView,
                               ProfileAvatarUpdateView,
                               ProfileCurrencyUpdateView,
                               MempoolUpdateView,
                               ElectrumInfoUpdateView)
from userprofile.views import APIKeyView
from userprofile.views import has_seen_welcome_popup

from hashtags.views import HashtagListView, HashtagUpdateView, LabelbaseProxyView


from .views import (
    UTXOsHealthView,
    LabelbaseHealthDatatableView,
    LabelbaseView,
    LabelbaseViewActionView,
    LabelbaseMergeView,
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
    DonationView,
    AboutView,
    EncryptionView,
    InteroperationalView,
    ExportLabelsView,
    # StatsAndKPIView,
    TreeMapsView,
    FixAndMergeLabelsView,
    LabelbaseDatatableView,
    #LabelbasePortfolioView,
    OutputStatUpdateRedirectView,
)

from importer.views import upload_labels
from django.contrib.auth import views as auth_views


urlpatterns = [
    path(
        "api/v0/labelbase/",
        LabelbaseAPIView.as_view()
    ),
    path(
        "api/v0/labelbase/<int:id>/",
        LabelbaseAPIView.as_view()
    ),
    path(
        "api/v0/labelbase/<int:labelbase_id>/label/",
        LabelAPIView.as_view()
    ),
    path(
        "api/v0/labelbase/<int:labelbase_id>/label/<int:id>/",
        LabelAPIView.as_view()
    ),
    path(
        "api-reference/",
        include_docs_urls(title="Labelbase API")
    ),
    path(
        "account/apikey/",
        login_required(APIKeyView.as_view()),
        name="apikey"
    ),
    path(
        "account/userprofile-avatar/",
        login_required(ProfileAvatarUpdateView.as_view()),
        name="userprofile_avatar",
    ),
    path(
        "account/userprofile-electrum/",
        login_required(ElectrumInfoUpdateView.as_view()),
        name="userprofile_electrum",
    ),
    path(
        "account/userprofile-mempool/",
        login_required(MempoolUpdateView.as_view()),
        name="userprofile_mempool",
    ),
    path(
        "account/userprofile-currency/",
        login_required(ProfileCurrencyUpdateView.as_view()),
        name="userprofile_currency",
    ),
    path(
        "account/userprofile/",
        login_required(ProfileView.as_view()),
        name="userprofile",
    ),
    path(
        "labelbase/<int:labelbase_id>/health/",
        login_required(UTXOsHealthView.as_view()),
        name="labelbase_health"
    ),
    path(
        "labelbase/<int:labelbase_id>/health/data/",
        login_required(LabelbaseHealthDatatableView.as_view()),
        name="labelbase_health_label_data"),
    path(
        "labelbase/<pk>/delete/",
        login_required(LabelbaseDeleteView.as_view()),
        name="del_labelbase"
    ),
    path(
        "labelbase/<int:labelbase_id>/",
        login_required(LabelbaseView.as_view()),
        name="labelbase"
    ),
    path(
        "labelbase/<int:labelbase_id>/hashtags/",
        login_required(HashtagListView.as_view()),
        name="labelbase_hashtags"
    ),
    path(
        "labelbase/<int:labelbase_id>/hashtags/proxy/",
        login_required(LabelbaseProxyView.as_view()),
        name="labelbase_hashtags_proxy"
    ),
    path(
        "labelbase/hashtag/<int:pk>/edit/",
        login_required(HashtagUpdateView.as_view()),
        name="hashtag_edit"
    ),
    path(
        "labelbase/<int:labelbase_id>/data/",
        login_required(LabelbaseDatatableView.as_view()),
        name="labelbase_label_data"),
    path(
        "labelbase/<int:labelbase_id>/actions/<str:action>/",
        login_required(LabelbaseViewActionView.as_view()),
        name="labelbase_actions"),
    path(
        "labelbase/<int:labelbase_id>/merge/",
        login_required(LabelbaseMergeView.as_view()),
        name="labelbase_merge"
    ),
    #path(
    #    "labelbase/<int:labelbase_id>/portfolio/",
    #    login_required(LabelbasePortfolioView.as_view()),
    #    name="labelbase_portfolio"
    #),
    path(
        "labelbase/<int:labelbase_id>/edit/",
        login_required(LabelbaseUpdateView.as_view()),
        name="edit_labelbase"
    ),
    path(
        "labelbase/import/",
        upload_labels,
        name="import_labels"
    ),
    path(
        "labelbase/<int:labelbase_id>/dyanmic-export/",
        login_required(ExportLabelsView.as_view()),
        name="labelbase_dynamic_export"
    ),
    path(
        "labelbase/<int:labelbase_id>/fix-and-manage/",
        login_required(FixAndMergeLabelsView.as_view()),
        name="labelbase_fix_and_manage"
    ),
    # path(
    #    "labelbase/<int:labelbase_id>/stats-and-kpi/",
    #    login_required(StatsAndKPIView.as_view()),
    #    name="labelbase_stats_and_kpi"
    # ),
    path(
        "labelbase/<int:pk>/tree-maps/",
        login_required(TreeMapsView.as_view()),
        name="labelbase_tree_maps"
    ),
    path(
        "labelbase/<int:pk>/tree-maps/<str:action>/",
        login_required(TreeMapsView.as_view()),
        name="labelbase_tree_maps"
    ),
    path(
        "labelbase/",
        login_required(LabelbaseFormView.as_view()),
        name="labelbase_new"
    ),
    path(
        "label/<int:pk>/edit/",
        login_required(LabelUpdateView.as_view()),
        name="edit_label"
    ),
    path(
        "label/<int:pk>/edit/<str:action>/",
        login_required(LabelUpdateView.as_view()),
        name="edit_label_with_action"
    ),
    path(
        "label/<int:pk>/delete/",
        login_required(LabelDeleteView.as_view()),
        name="del_label"
    ),
    path(
        "account/logout/",
        LogoutView.as_view(),
        name="logout"
    ),
    path(
        "account/register/",
        RegistrationView.as_view(),
        name="registration"
    ),
    path(
        "account/register/done/",
        RegistrationCompleteView.as_view(),
        name="registration_complete"
    ),
    path(
        "account/change-password/",
        auth_views.PasswordChangeView.as_view(
            template_name="change_password.html",
            success_url="/"
        ),
        name="change_password"
    ),
    path(
        "privacy-policy",
        PrivacyView.as_view(),
        name="privacy_policy"
    ),
    path(
        "terms",
        TermsView.as_view(),
        name="terms"
    ),
    path(
        "donate",
        DonationView.as_view(),
        name="donate"
    ),
    path(
        "about",
        AboutView.as_view(),
        name="about"
    ),
    path(
        "encryption",
        EncryptionView.as_view(),
        name="encryption"
    ),
    path(
        "interoperational",
        InteroperationalView.as_view(),
        name="interoperational"
    ),
    path(
        "outputstat/<int:output_stats_id>/update/<int:label_id>/",
        login_required(OutputStatUpdateRedirectView.as_view()),
        name='outputstat_update_redirect'
    ),
    path(
        "",
        HomeView.as_view(),
        name="home"
    ),
    path(
        "",
        include(tf_urls)
    ),
    path(
        "knowledge-base/",
        include('knowledge_base.urls')
    ),
    path(
        "",
        include("user_sessions.urls", "user_sessions")
    ),
    path(
        "attachments/",
        include('attachments.urls', namespace='attachments')
    ),
    path(
        "has_seen_welcome_popup/",
        has_seen_welcome_popup,
        name='has_seen_welcome_popup'
    ),

]

urlpatterns.append(path("admin/", admin.site.urls))
