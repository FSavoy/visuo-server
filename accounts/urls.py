from django.conf.urls import url
from django.contrib.auth.views import login, logout, password_change, password_change_done
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^login/$', login, {'template_name': 'accounts/login.html'}),
    url(r'^logout/$', logout, {'next_page': '/'}),
    url(r'^password_change/$', password_change, {'template_name': 'accounts/password_change_form.html', 'post_change_redirect': '/accounts/password_change_done/'}),
    url(r'^password_change_done/$', password_change_done, {'template_name': 'accounts/password_change_done.html'}),
    url(r'^profile', RedirectView.as_view(url = '/')),
]