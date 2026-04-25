from django.db import models
from django.utils.text import slugify


class BookTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Book Tag'
        verbose_name_plural = 'Book Tags'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    edition_number = models.IntegerField()
    writer = models.CharField(max_length=200)
    link = models.URLField()
    tags = models.ManyToManyField(BookTag, blank=True, related_name='books')

    def __str__(self):
        return f"{self.title} (Ed. {self.edition_number})"
