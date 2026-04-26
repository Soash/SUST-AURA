from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from thesis.models import ResearchWork
from publication.models import Publication


class StaticViewSitemap(Sitemap):
    """Covers all static / list pages."""
    priority   = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'home',
            'about',
            'book_list',
            'thesis_list',
            'publication_list',
        ]

    def location(self, item):
        return reverse(item)


class ThesisSitemap(Sitemap):
    """One URL per public research work."""
    changefreq = 'monthly'
    priority   = 0.6

    def items(self):
        return ResearchWork.objects.filter(is_public=True)

    def lastmod(self, obj):
        return obj.uploaded_at

    def location(self, obj):
        return reverse('thesis_detail', kwargs={'pk': obj.pk})


class PublicationSitemap(Sitemap):
    """One URL per public publication."""
    changefreq = 'monthly'
    priority   = 0.6

    def items(self):
        return Publication.objects.filter(is_public=True)

    def lastmod(self, obj):
        return obj.uploaded_at

    def location(self, obj):
        return reverse('publication_detail', kwargs={'pk': obj.pk})


sitemaps = {
    'static':      StaticViewSitemap,
    'thesis':      ThesisSitemap,
    'publication': PublicationSitemap,
}
