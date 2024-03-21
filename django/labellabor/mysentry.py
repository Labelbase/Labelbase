import logging
logger = logging.getLogger('labelbase')

class MyEventScrubber:
    def scrub_event(self, event):
        # Scrub IP from request environment
        if 'request' in event and 'env' in event['request'] and 'REMOTE_ADDR' in event['request']['env']:
            event['request']['env']['REMOTE_ADDR'] = '0.0.0.0'

        # Scrub IP from user information
        if 'user' in event and 'ip_address' in event['user']:
            event['user']['ip_address'] = '0.0.0.0'

def before_send(event, hint):
    try:
        from django.contrib.auth.models import User # keep import here
        user_data = event.get('user', {})
        user_id = user_data.get('id', 0)
        if User.objects.filter(id=user_id).exists():
            user = User.objects.get(id=user_id)
            if user.profile.use_sentry:
                event_scrubber = MyEventScrubber()
                event_scrubber.scrub_event(event)
                #print(f"return event {event} for {user_id}")
                return event
            return None
    except Exception as e:
        print(e)
    return event
