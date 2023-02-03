from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, resolve_url
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, TemplateView
from django.views.generic.list import ListView
from two_factor.views import OTPRequiredMixin
from two_factor.views.utils import class_view_decorator

from labelbase.models import Label, Labelbase
from labelbase.forms import LabelForm
from django.http import HttpResponse

class HomeView(TemplateView):
    template_name = 'home.html'


class LabelbaseView(ListView):
    template_name = 'labelbase.html'
    context_object_name = 'label_list'
    def get_queryset(self):
        qs = Label.objects.filter(labelbase__user_id=self.request.user.id, labelbase_id=self.kwargs['labelbase_id'])
        return qs.order_by("-id")

    def get_context_data(self, **kwargs):
        context = super(LabelbaseView, self).get_context_data(**kwargs)
        context['labelbase'] = Labelbase.objects.filter(id=self.kwargs['labelbase_id'], user_id=self.request.user.id).first()
        context['labelform'] = LabelForm(request=self.request)
        return context

    def post(self, request, *args, **kwargs):
        labelform = LabelForm(request.POST, request=request)
        if labelform.is_valid():
            labelform.save()
        # success massage
        # error message

        return HttpResponse(labelform.labelbase.get_absolute_url())





class RegistrationView(FormView):
    template_name = 'registration.html'
    form_class = UserCreationForm

    def form_valid(self, form):
        form.save()
        return redirect('registration_complete')


class RegistrationCompleteView(TemplateView):
    template_name = 'registration_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_url'] = resolve_url(settings.LOGIN_URL)
        return context


@class_view_decorator(never_cache)
class ExampleSecretView(OTPRequiredMixin, TemplateView):
    template_name = 'secret.html'
