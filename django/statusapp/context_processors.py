from .models import StatusMessage

def latest_status_message(request):
    try:
        latest_message = StatusMessage.objects.latest('created_at')
    except StatusMessage.DoesNotExist:
        latest_message = None
    return {'latest_status_message': latest_message}
