from django.db import models

class LogEntry(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return f'LogEntry(id={self.id}) at {self.created_at} with message "{self.message}"'