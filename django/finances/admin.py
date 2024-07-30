from django.contrib import admin
from .models import OutputStat, HistoricalPrice

class OutputStatAdmin(admin.ModelAdmin):
    list_display = ('type_ref_hash',
                    'value',
                    'confirmed_at_block_height',
                    'confirmed_at_block_time',
                    'get_spent_status',
                    'spent',
                    'network',
                    'user',
                    'next_enc_input_attrs',
                    'last_error')
    list_filter = ('network', 'spent')
    search_fields = ('type_ref_hash',)
    ordering = ('-confirmed_at_block_time',)

class HistoricalPriceAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'usd_price', 'eur_price', 'gbp_price')
    search_fields = ('timestamp',)
    ordering = ('-timestamp',)

admin.site.register(OutputStat, OutputStatAdmin)
admin.site.register(HistoricalPrice, HistoricalPriceAdmin)
