"""jiaotongweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import url
from django.contrib import admin
from chart import views
from django.conf import settings
from django.conf.urls.static import static
import math
import random


admin.autodiscover()

t=random.random()
t=str(t)
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',views.homehtml),
    url(r'^flowchart/show/$', views.Show_picture),
    url(r'^map/show/$', views.sectorShow_picture),
    url(r'^flowchart/$',views.Get_Date),
    url(r'^map/$',views.sectorGetDate),
    url(r'^datacheck/$',views.datacheck_GetData),
    url(r'^datacheck/show/$',views.datacheck_show),
    url(r'^detection/$',views.detection_GetData),
    url(r'^phasecheck/$',views.phasecheck_GetData),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# urlpatterns = [
#     url(r'^admin/', admin.site.urls),
#     url(r'^$',views.homehtml),
#     url(r'^flowchart/show/$', views.Show_picture),
#     url(r'^flowchart/$',views.Get_Date),
# ]+static('',url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT, }),
#    )
handler404=views.page_not_found
