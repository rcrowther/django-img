from django.conf.urls import url

from image.views.serve import serve

urlpatterns = [
    url(r'^([^/]*)/(\d*)/([^/]*)/[^/]*$', serve, name='image_serve'),
]
