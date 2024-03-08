from django.contrib import admin
from .models import Category, Article, ExportSnapshot

admin.site.register(ExportSnapshot)
admin.site.register(Category)
admin.site.register(Article)
