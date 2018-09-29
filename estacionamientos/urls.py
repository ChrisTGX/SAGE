# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from estacionamientos import views


urlpatterns = patterns('',
    url(r'^$', views.estacionamientos_all, name = 'estacionamientos_all'),
    url(r'^(?P<_id>\d+)/$', views.estacionamiento_detail, name = 'estacionamiento_detail'),
    url(r'^(?P<_id>\d+)/reserva$', views.estacionamiento_reserva, name = 'estacionamiento_reserva'),
    url(r'^\d+/pagar_reserva', views.pagar_reserva, name = 'pagar_reserva'),
    url(r'^\d+/print_report', views.print_report, name = 'print_report'),
    url(r'^(?P<_id>\d+)/tasa_reservacion', views.tasa_reservacion, name = 'tasa_reservacion'),
    url(r'^(?P<template>ingresos)', views.login, name = 'login'),
    url(r'^(?P<template>reservaciones)', views.login, name = 'login'), 
)
