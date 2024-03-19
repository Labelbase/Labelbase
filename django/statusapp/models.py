from django.db import models

class StatusMessage(models.Model):
    message = models.CharField(max_length=1000)
    color = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
