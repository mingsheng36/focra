from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^create$', views.createCrawler, name='createCrawler'),
    url(r'^start$', views.startCrawl, name='startCrawl'),
    url(r'^stop$', views.stopCrawl, name='stopCrawl'),
    url(r'^delete$', views.deleteCrawler, name='deleteCrawler'),
    url(r'^(?P<username>\w+)$', views.overview, name='overview'),
    url(r'^(?P<username>\w+)/(?P<crawlerName>\w+)', views.monitor, name='monitor'),
    #url(r'^fetch$', views.fetch, name='fetch'),
)
