import re
from .models import Hashtag
from labelbase.models import Label
from background_task import background

@background(schedule=1)
def store_hashtags_as_objects(labelbase_id, loop=None):
    for obj in Label.objects.filter(labelbase_id=labelbase_id):
        hashtags = re.findall(r'#\w+', obj.label)
        for tag in hashtags:
            clean_tag = re.search(r'#(\w+)', tag).group(1)
            hts = Hashtag.objects.filter(labelbase_id=labelbase_id)
            found = False
            for ht in hts:
                if ht.name == clean_tag:
                    found = True
                    break
            if not found:
                hashtag = Hashtag(name=clean_tag, labelbase_id=labelbase_id)
                hashtag.save()
