from __future__ import unicode_literals

from django.contrib.contenttypes.admin import GenericStackedInline



from django.contrib import admin
from .models import LabelAttachment
from .models import Attachment

class AttachmentInlines(GenericStackedInline):
    model = Attachment
    exclude = ()
    extra = 1






admin.site.register(LabelAttachment) 
