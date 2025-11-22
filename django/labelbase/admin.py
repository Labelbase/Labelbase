from django.contrib import admin
from .models import Labelbase
from .models import Label
from django.conf import settings

class LabelbaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'network', 'operation_mode']
    list_filter = ['network', 'operation_mode']
    search_fields = ['name', 'fingerprint']


class LabelAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'labelbase', 'label']
    list_filter = ['type', 'labelbase__network']
    search_fields = ['ref', 'label']

    # Organize fields into logical sections
    fieldsets = (
        ('Core BIP-329 Fields', {
            'fields': ('labelbase', 'type', 'ref', 'label', 'origin', 'spendable')
        }),
        ('Additional BIP-329 Fields', {
            'fields': ('height', 'time', 'fee', 'value', 'rate', 'keypath', 'fmv', 'heights'),
            'classes': ('collapse',),  # Make this section collapsible
        }),
        ('Internal', {
            'fields': ('type_ref_hash',),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ['type_ref_hash']

if settings.DEBUG:
    admin.site.register(Labelbase, LabelbaseAdmin)
    admin.site.register(Label, LabelAdmin)
