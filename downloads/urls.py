from django.conf.urls import url

from downloads import views

urlpatterns = [
    url(r'^$', views.index, name='downloads'),
]