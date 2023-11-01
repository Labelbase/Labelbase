from django.views.generic import TemplateView
from rest_framework.authtoken.models import Token
from django.http import JsonResponse


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
            except Exception as ex:
                pass
        return JsonResponse({'message': 'Invalid request.'}, status=400)


class APIKeyView(TemplateView):
    """ """
    template_name = "apikey.html"

    def get_context_data(self, **kwargs):
        context = super(APIKeyView, self).get_context_data(**kwargs)
        context["api_token"] = Token.objects.get(user_id=self.request.user.id)
        return context
