from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from labelbase.models import Labelbase

from .forms import UploadFileForm
from .tasks import process_uploaded_data
from .models import UploadedData


@login_required
def upload_labels(request):
    """
    Used to import labels manually using files.
    """
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            labelbase = get_object_or_404(
                Labelbase,
                id=form.cleaned_data.get("labelbase_id", ""),
                user_id=request.user.id,
            )
            uploaded_data = UploadedData.objects.create(
                user=request.user,
                labelbase=labelbase,
                import_type=form.cleaned_data.get("import_type", ""),
                file=request.FILES["file"],
            )
            # Schedule the background task to process the uploaded data
            process_uploaded_data(uploaded_data.id)
            messages.add_message(
                request,
                messages.INFO,
                "Task scheduled successfully.",
#               "Task scheduled successfully. You will be notified upon completion.",
            )
            return HttpResponseRedirect(labelbase.get_absolute_url())
    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form": form})
