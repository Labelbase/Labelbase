from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import tempfile
import os
import json
from labelbase.models import Labelbase, Label
from labelbase.serializers import LabelSerializer
from django.shortcuts import get_object_or_404

from .forms import UploadFileForm
from tempfile import NamedTemporaryFile



def handle_uploaded_file(f):
    fp = NamedTemporaryFile(delete=False)
    for chunk in f.chunks():
        fp.write(chunk)
    return fp


@login_required
def upload_labels(request):
    """
    Used to import labels manually using files.
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            labelbase = get_object_or_404(Labelbase, id=form.cleaned_data.get('labelbase_id', ''), user_id=request.user.id)
            fp = handle_uploaded_file(request.FILES['file'])
            fp.seek(0)
            if form.cleaned_data.get('import_type', '') == 'BIP-0329':
                while True:
                    buf = f.readline()
                    if buf == '':
                        break
                    data = json.loads(buf)
                    data['labelbase'] = labelbase.id
                    serializer = LabelSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
            else:
                fp.close()
                os.unlink(fp.name)
                return HttpResponseRedirect('/failed/url/')
            fp.close()
            os.unlink(fp.name)

    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
