from django.db import models
from django.utils.text import slugify

from django.utils import timezone
from jsonfield import JSONField


class ExportSnapshot(models.Model):
    exported_data = JSONField(default={})
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Export Snapshot {self.timestamp}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    exclude_from_export = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        #self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=100)
    exclude_from_export = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        #self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
