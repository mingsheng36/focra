from django.conf.urls import patterns, include, url
from django.contrib import admin
import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Focra.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^start/$', views.startCrawl, name='startCrawl'),
    url(r'^stop/$', views.stopCrawl, name='stopCrawl'),
    url(r'^home/$', views.home, name='home'),
    url(r'^create/$', views.createCrawler, name='createCrawler'),
    url(r'^retrieve/$', views.retrieveCrawlers, name='retrieveCrwalers'),
    url(r'^update/$', views.updateCrawler, name='updateCrawler'),
    url(r'^delete/$', views.deleteCrawler, name='deleteCrawler'),
)
