from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import sitemaps
from core.views import robots_txt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('users.urls')),
    path('thesis/', include('thesis.urls')),
    path('book/', include('book.urls')),
    path('publications/', include('publication.urls')),
    path('tinymce/', include('tinymce.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
