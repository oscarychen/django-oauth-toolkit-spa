from django.contrib import admin
from django.urls import include, path


admin.autodiscover()


urlpatterns = [
    path("auth/", include("oauth_toolkit_spa.urls"))
]
