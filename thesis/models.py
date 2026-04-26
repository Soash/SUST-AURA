from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils import timezone


class ResearchWork(models.Model):
    WORK_TYPES = [
        ('HONOURS_THESIS', 'Honours Thesis'),
        ('HONOURS_PROJECT', 'Honours Project'),
        ('MASTERS_THESIS', 'Masters Thesis'),
        ('MASTERS_PROJECT', 'Masters Project'),
        ('PhD_THESIS', 'PhD Thesis'),
        ('PhD_PROJECT', 'PhD Project'),
    ]

    title           = models.CharField(max_length=500)
    abstract        = models.TextField()
    authors         = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='authored_works')
    supervisor_name = models.TextField()  # Manual entry since teachers don't interact
    work_type       = models.CharField(max_length=20, choices=WORK_TYPES)
    link            = models.URLField()
    uploaded_at     = models.DateTimeField(auto_now_add=True)
    is_public       = models.BooleanField(default=True)

    # Embargo: if set, the full document link is hidden until this date
    embargo_until   = models.DateField(
        null=True, blank=True,
        help_text="If set, the document link is hidden until this date."
    )

    @property
    def is_currently_embargoed(self):
        """Returns True if today's date is still before the embargo lift date."""
        if self.embargo_until:
            return timezone.now().date() < self.embargo_until
        return False

    def __str__(self):
        return self.title


class Report(models.Model):
    work        = models.ForeignKey(ResearchWork, on_delete=models.CASCADE, related_name='reports')
    reporter    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason      = models.TextField()
    timestamp   = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report on {self.work.title} by {self.reporter.username}"


class ThesisAccessLog(models.Model):
    """
    Records every time a user follows the tracked document link.
    Used for analytics and audit trails.
    """
    user        = models.ForeignKey(
                      settings.AUTH_USER_MODEL,
                      on_delete=models.SET_NULL,
                      null=True,
                      related_name='thesis_access_logs',
                  )
    thesis      = models.ForeignKey(
                      ResearchWork,
                      on_delete=models.CASCADE,
                      related_name='access_logs',
                  )
    accessed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-accessed_at']

    def __str__(self):
        return f"{self.user} accessed '{self.thesis.title}' at {self.accessed_at:%Y-%m-%d %H:%M}"



