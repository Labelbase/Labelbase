from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm


def upload_labels(request):
    """
    Used to import labels manually using files.
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            #handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
