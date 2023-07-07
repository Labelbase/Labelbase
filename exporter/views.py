import json
from django.http import StreamingHttpResponse
from labelbase.models import Labelbase, Label
from django.contrib.auth.decorators import login_required


@login_required
def stream_labels_as_jsonl(request, labelbase_id):
    """
    Google Chrome blocks downloads that it considers to be potentially dangerous or harmful to your computer. If you are trying to download a file that Chrome is blocking, there are a few ways to resolve the issue:

        Whitelist the site: If you trust the site from which you are downloading the file, you can add it to your list of trusted sites in Chrome. To do this, go to the site, click the lock icon in the address bar, and then click "Site settings". In the "Permissions" section, click "Downloads", and then toggle the switch next to "Block dangerous and deceptive downloads" to "Off".

        Download the file in Incognito mode: Chrome blocks downloads based on your browsing history, so downloading the file in Incognito mode may bypass the block. To open an Incognito window, click the three dots in the upper-right corner of Chrome, and then click "New incognito window".

        Change the file extension: Sometimes, changing the file extension from .exe or .zip to .txt, for example, can help bypass the block. However, this may not always work, and the file may still be harmful even if the extension is changed.

        Use a different browser: If none of the above methods work, you can try downloading the file using a different browser, such as Mozilla Firefox or Microsoft Edge.

    Keep in mind that Chrome's download protection is in place to help keep your computer safe, so only download files from sources that you trust. If you are unsure whether a file is safe, it's always a good idea to scan it with an antivirus program before downloading.
    """

    def get_queryset():
        qs = Label.objects.filter(
            labelbase__user_id=request.user.id, labelbase_id=labelbase_id
        ).values("type", "ref", "label")
        return qs.order_by("id")

    def generator():
        for item in get_queryset():
            yield json.dumps(item) + "\n"

    # Return the data as a streaming response
    response = StreamingHttpResponse(generator(), content_type="application/json")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="labelbase-{}.jsonl"'.format(labelbase_id)
    return response
