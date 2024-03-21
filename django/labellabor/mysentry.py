from sentry_sdk.scrubber import EventScrubber, DEFAULT_DENYLIST

# https://docs.sentry.io/platforms/python/data-management/sensitive-data/
# https://docs.sentry.io/platforms/python/configuration/filtering/
# Define your custom denylist if needed
custom_denylist = DEFAULT_DENYLIST # + ['custom_sensitive_key']
event_scrubber = EventScrubber(denylist=custom_denylist)

def before_send(event, hint):
    try:
        from django.contrib.auth.models import User # keep import here
        user_data = event.get('user', {})
        user_id = user_data.get('id', 'No User ID')
        user = User.objects.get(id=user_id)
        # Check user's preference for error tracking
        if user.profile.use_sentry:
            event_scrubber.scrub_event(event)
            print(event)
            print ("return event {}".format(event))
            return event
    except Exception as e:
        print(e)
        pass
    return None
