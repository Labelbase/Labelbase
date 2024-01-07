from django.contrib import admin
from .models import HistoricalPrice, OutputStat

admin.site.register(OutputStat)
admin.site.register(HistoricalPrice)
