from django.urls import include, path
from core.admin import portal_admin_site

urlpatterns = [path('manage/', portal_admin_site.urls), path('', include('core.urls'))]
