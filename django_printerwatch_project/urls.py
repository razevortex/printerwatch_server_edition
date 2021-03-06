"""django_printerwatch_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import subprocess as sp
from subprocess import Popen

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/', include('mainframe.urls')),
    #path('monitor/', include('printer_monitor.urls')),
    path('cartridges/', include('running_out.urls')),
    path('subsite/', include('subs.urls')),
    path('sandbox/', include('dev_sandbox.urls')),
]
