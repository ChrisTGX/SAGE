# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', RedirectView.as_view(url='estacionamientos/')),
    url(r'^estacionamientos/', include('estacionamientos.urls',namespace='estacionamientos')),
)