from django.db import models
from django.conf import settings


class Publication(models.Model):
    TYPE_CHOICES = [
        ('journal',     'Journal Article'),
        ('conference',  'Conference Paper'),
        ('book_chapter','Book Chapter'),
        ('preprint',    'Preprint'),
        ('technical',   'Technical Report'),
        ('other',       'Other'),
    ]

    title        = models.CharField(max_length=500)
    abstract     = models.TextField(blank=True)
    pub_type     = models.CharField(max_length=20, choices=TYPE_CHOICES, default='journal')
    authors      = models.ManyToManyField(
                       settings.AUTH_USER_MODEL,
                       related_name='publications',
                       blank=True,
                   )
    external_authors = models.TextField(
                       blank=True,
                       help_text="Comma-separated names of co-authors not on the platform."
                   )
    journal_name = models.CharField(max_length=300, blank=True, help_text="Journal or conference name")
    year         = models.PositiveIntegerField(null=True, blank=True)
    doi          = models.CharField(max_length=200, blank=True, help_text="e.g. 10.1000/xyz123")
    link         = models.URLField(blank=True, help_text="External URL (journal site, arXiv, etc.)")
    uploaded_by  = models.ForeignKey(
                       settings.AUTH_USER_MODEL,
                       on_delete=models.SET_NULL,
                       null=True,
                       related_name='uploaded_publications',
                   )
    uploaded_at  = models.DateTimeField(auto_now_add=True)
    is_public    = models.BooleanField(default=True)

    class Meta:
        ordering = ['-year', '-uploaded_at']

    def __str__(self):
        return self.title

    def doi_url(self):
        if self.doi:
            return f"https://doi.org/{self.doi}"
        return None
