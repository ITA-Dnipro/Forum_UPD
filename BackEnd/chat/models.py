from django.db import models


class Chat(models.Model):
    message = models.CharField(max_length=150)

    def __str__(self):
        return f"Message id: {self.id}, message text: {self.message}"
