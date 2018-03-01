from django.conf.urls import url

from . import views

app_name = 'tema1app'
urlpatterns = [
    url('^$', views.index, name='index'),
    url('getdata', views.getdata, name="getdata"),
]