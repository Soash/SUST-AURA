from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')

def robots_txt(request):
    sitemap_url = request.build_absolute_uri('/sitemap.xml')
    content = f"""User-agent: *
Allow: /

# Private / auth areas
Disallow: /admin/
Disallow: /signup/
Disallow: /accounts/login/
Disallow: /logout/
Disallow: /password-reset/
Disallow: /profile/edit/
Disallow: /staff/

# Sitemap
Sitemap: {sitemap_url}
"""
    return HttpResponse(content, content_type='text/plain')
