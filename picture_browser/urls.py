from django.conf.urls import url
from picture_browser import views

urlpatterns = [
    # ex : /2013/12/10/
    url(r'^(?P<page>\d+)/$', views.index, name='index_page'),
    # ex : /
    url(r'^$', views.index, name='index'),
]