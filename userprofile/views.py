from django.shortcuts import render
from django.views.generic import TemplateView  # FormView,
from rest_framework.authtoken.models import Token


class ProfileView(TemplateView):
    """ """

    template_name = "profile.html"


class APIKeyView(TemplateView):
    """ """

    template_name = "apikey.html"

    def get_context_data(self, **kwargs):
        context = super(APIKeyView, self).get_context_data(**kwargs)
        context["api_token"] = Token.objects.get(user_id=self.request.user.id)
        return context
