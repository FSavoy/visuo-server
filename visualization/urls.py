from django.conf.urls import url

from visualization import views

urlpatterns = [
    url(r'^(?P<shift>-?\d+)$', views.show_image, name='show_image_shift'),
    url(r'^$', views.show_image, name='show_image'),
]
