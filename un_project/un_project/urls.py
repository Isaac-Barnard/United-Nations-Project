"""un_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('minecraft/records/admin/', admin.site.urls),

    path('', include('website.urls')),
    
    path('minecraft/records/', include('un_app.urls')),   # Main app URLs
    path('minecraft/records/', include('un_records_app.urls')),   # Main app URLs

    path('minecraft/records/un_api/', include('un_api.urls')),  # API URLs
    path('minecraft/player/api/', include('players_api.urls'))
]



from django.conf import settings
from django.conf.urls.static import static
# Add this to serve media files during development
if settings.MEDIA_URL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)