from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    edition_number = models.IntegerField()
    writer = models.CharField(max_length=200)
    link = models.URLField()

    def __str__(self):
        return f"{self.title} (Ed. {self.edition_number})"
