"""unimelbPublications URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls import url
from django.urls import path,re_path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),

    re_path(r'^$', views.homepage),
    re_path(r'^homepage/$', views.homepage, name='homepage'),
    re_path(r'^overview/$', views.overview, name='overview'),
    re_path(r'^authorCandidate/(.+)$', views.authorcandidate, name='authorcandidate'),
    re_path(r'^paperDetails/(.+)$', views.paperDetails, name='paperdetails'),
    re_path(r'^authorDetails/(.+)$', views.authorDetails, name='authordetails'),
    re_path(r'^coAuthorDetails/(.+)$', views.coAuthorDetails, name='coauthordetails'),
    re_path(r'^paperCandidate/(.+)$', views.paperCandidate, name='papercandidate'),
    re_path(r'^coAuthoredPapers/(.+)/(.+)$', views.coAuthoredPapers, name='coauthoredpapers'),
    re_path(r'^keywordsCandidate/(.+)$', views.searchKeywords, name='searchKeyword')
    url(r'^yearly_trend', views.yearly_trend, name='yearly_trend')
]
