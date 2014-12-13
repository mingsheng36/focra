from django.conf.urls import patterns, include, url
from django.contrib import admin
import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'focra.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^start/$', views.startCrawl, name='startCrawl'),
    url(r'^stop/$', views.stopCrawl, name='stopCrawl'),
    url(r'^overview/$', views.overview, name='overview'),
    url(r'^create/$', views.createCrawler, name='createCrawler'),

)
