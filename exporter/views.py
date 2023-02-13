import json
from django.http import StreamingHttpResponse
from labelbase.models import Labelbase, Label
from django.contrib.auth.decorators import login_required

@login_required
def stream_labels_as_jsonl(request, labelbase_id):

    def get_queryset():
        qs = Label.objects.filter(labelbase__user_id=request.user.id,
                                    labelbase_id=labelbase_id).values_list(
                                        'id', 'type', 'ref', 'label')
        return qs.order_by("id")

    def generator():
        for item in get_queryset():
            yield json.dumps(item) + '\n'

    # Return the data as a streaming response
    response = StreamingHttpResponse(generator(), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="labelbase-{}.jsonl"'.format(labelbase_id)
    return response
