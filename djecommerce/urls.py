from django.contrib import admin
from django.urls import path,include
from django.conf import settings

# from . views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('/sbt', include('core.urls')),

]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__', include(debug_toolbar.urls))]