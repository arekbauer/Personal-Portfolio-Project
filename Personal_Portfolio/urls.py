"""
URL configuration for personal_portfolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from portfolio import views 

urlpatterns = [
    # Website URLs
    path('api/now-playing/', views.get_now_playing, name='now-playing'),
    path('secret-admin/', admin.site.urls),
    path('recipes/', include('recipes.urls')),
    path('albums/', views.albums, name='albums'),
    path('slabs/', views.pokemon_slabs, name='pokemon-collection'),
    path('', views.home, name = 'home'),
    
    # Include TRMNL service URLs
    path('api/trmnl/', include('trmnl_service.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
