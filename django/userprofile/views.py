from django.views.generic import TemplateView
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import UpdateView
from django.contrib import messages
from .models import Profile

from .forms import (
    ProfileAvatarForm,
    ProfileCurrencyForm,
    ElectrumServerInfoForm,
    MempoolForm,
    ProfileFeeForm)



from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Profile

@require_POST
@login_required
def has_seen_welcome_popup(request):
    profile = Profile.objects.get(user=request.user)
    profile.has_seen_welcome_popup = True
    profile.save()
    return JsonResponse({'status': 'success'})


class ProfileView(TemplateView):
    """ """
    template_name = "profile.html"

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            toggle_id = request.POST.get('toggleId', None)
            toggle_value = request.POST.get('toggleValue', None)
            try:
                setattr(request.user.profile, toggle_id, toggle_value == "true")
                request.user.profile.save()
                return JsonResponse({'message': 'Settings updated successfully.'})
            except Exception:
                pass
        return JsonResponse({'message': 'Invalid request.'}, status=400)


class APIKeyView(TemplateView):
    """ """
    template_name = "apikey.html"

    def get_context_data(self, **kwargs):
        context = super(APIKeyView, self).get_context_data(**kwargs)
        context["api_token"] = Token.objects.get(user_id=self.request.user.id)
        return context


class ProfileAvatarUpdateView(UpdateView):
    model = Profile
    form_class = ProfileAvatarForm
    template_name = 'profile_update_avatar.html'

    def get_success_url(self):
        return reverse_lazy('userprofile_avatar')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def form_valid(self, form):
        profile = form.save(commit=False)
        if not profile.avatar_url:
            profile.avatar_url = profile._meta.get_field('avatar_url').get_default()
        profile.save()
        messages.success(self.request, "<strong>Success!</strong> Avatar updated successfully.")
        return super().form_valid(form)


class ElectrumInfoUpdateView(UpdateView):
    model = Profile
    form_class = ElectrumServerInfoForm
    template_name = 'electrum_server_info_update.html'

    def get_success_url(self):
        return reverse_lazy('userprofile_electrum')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def form_valid(self, form):
        profile = form.save(commit=False)
        if not profile.electrum_hostname:
            profile.electrum_hostname = profile._meta.get_field('electrum_hostname').get_default()
        if not profile.electrum_ports:
            profile.electrum_ports = profile._meta.get_field('electrum_ports').get_default()
        if not profile.electrum_hostname_test:
            profile.electrum_hostname_test = profile._meta.get_field('electrum_hostname_test').get_default()
        if not profile.electrum_ports_test:
            profile.electrum_ports_test = profile._meta.get_field('electrum_ports_test').get_default()
        profile.save()
        messages.success(self.request, "<strong>Success!</strong> Electrum ServerInfo updated successfully.")
        return super().form_valid(form)


class MempoolUpdateView(UpdateView):
    model = Profile
    form_class = MempoolForm
    template_name = 'mempool_update.html'

    def get_success_url(self):
        return reverse_lazy('userprofile_mempool')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def form_valid(self, form):
        profile = form.save(commit=False)
        if not profile.mempool_endpoint:
            profile.mempool_endpoint = profile._meta.get_field('mempool_endpoint').get_default()
        profile.save()
        messages.success(self.request, "<strong>Success!</strong> Mempool endpoint updated successfully.")
        return super().form_valid(form)


class ProfileCurrencyUpdateView(UpdateView):
    model = Profile
    form_class = ProfileCurrencyForm
    template_name = 'profile_update_currency.html'

    def get_success_url(self):
        return reverse_lazy('userprofile_currency')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "<strong>Success!</strong> Currency updated successfully.")
        return super().form_valid(form)


class ProfileFeeUpdateView(UpdateView):
    model = Profile
    form_class = ProfileFeeForm
    template_name = 'profile_update_fees.html'

    def get_success_url(self):
        return reverse_lazy('userprofile_fees')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "<strong>Success!</strong> Fees updated successfully.")
        return super().form_valid(form)
