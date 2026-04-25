from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')), 
    path('', include('users.urls')), 
    path('thesis/', include('thesis.urls')),
    path('book/', include('book.urls')),
    path('tinymce/', include('tinymce.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
