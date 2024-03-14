from django.views.generic import ListView
from django.views.generic.edit import UpdateView
from django.views import View
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages

from labelbase.models import Labelbase
from .tasks import store_hashtags_as_objects
from .models import Hashtag


class LabelbaseProxyView(View):
    def get(self, request, *args, **kwargs):
        labelbase_id = kwargs.get('labelbase_id')
        labelbase = get_object_or_404(Labelbase, id=labelbase_id,
                                        user_id=request.user.id)
        if request.GET.get('sync', 'no') == 'yes':
            store_hashtags_as_objects(labelbase_id)
            messages.add_message(
                request,
                messages.INFO,
                "<strong>Processing Hashtags!</strong> Please wait briefly and refresh your page.", 
            )
        return HttpResponseRedirect(labelbase.get_hashtags_url())

class HashtagListView(ListView):
    model = Hashtag
    template_name = 'hashtags/labelbase_list.html'

    def get_queryset(self):
        labelbase_id = self.kwargs['labelbase_id']
        labelbase = get_object_or_404(
            Labelbase, id=labelbase_id, user_id=self.request.user.id
        )
        queryset = Hashtag.objects.filter(labelbase_id=labelbase_id,
                                        labelbase__user_id=self.request.user.id).order_by('-name')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(HashtagListView, self).get_context_data(**kwargs)
        context["active_labelbase_id"] = self.kwargs['labelbase_id']
        context["labelbase"] = get_object_or_404(
            Labelbase, id=self.kwargs['labelbase_id'], user_id=self.request.user.id
        )
        return context


class HashtagUpdateView(UpdateView):
    model = Hashtag
    fields = ['name', 'description']
    template_name = 'hashtags/labelbase_edit.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.id != self.get_object().labelbase.user_id:
            return HttpResponseForbidden("You do not have permission to edit this hashtag.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        labelbase_id = self.object.labelbase_id
        return reverse('labelbase_hashtags', kwargs={'labelbase_id': labelbase_id})

    def get_context_data(self, **kwargs):
        labelbase_id = self.get_object().labelbase.id
        context = super(HashtagUpdateView, self).get_context_data(**kwargs)
        context["active_labelbase_id"] = labelbase_id
        context["labelbase"] = get_object_or_404(
            Labelbase, id=labelbase_id, user_id=self.request.user.id
        )
        return context
