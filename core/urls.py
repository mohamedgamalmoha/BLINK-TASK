"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView,
                                   SpectacularJSONAPIView, SpectacularYAMLAPIView)

from accounts.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.api.urls'), name='accounts'),
    path('api/', include('loans.api.urls'), name='loans'),
    path('api/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/schema/yaml/', SpectacularJSONAPIView.as_view(), name='schema_yaml_view'),
    path('api/docs/schema/json/', SpectacularYAMLAPIView.as_view(), name='schema_json_view'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(), name='redoc_docs_view'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(), name='swagger_docs_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^.*$', HomeView.as_view(), name='home')
]
