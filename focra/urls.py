from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^register$', views.register, name='register'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^create$', views.createCrawler, name='createCrawler'),
    url(r'^start$', views.startCrawl, name='startCrawl'),
    url(r'^stop$', views.stopCrawl, name='stopCrawl'),
    url(r'^pause$', views.pauseCrawl, name='pauseCrawl'),
    url(r'^resume$', views.resumeCrawl, name='resumeCrawl'),
    url(r'^delete$', views.deleteCrawler, name='deleteCrawler'),
    url(r'^fetch$', views.fetch, name='fetch'),
    url(r'^data$', views.data, name='data'),
    url(r'^check$', views.check_name, name='check_name'),
    url(r'^stats$', views.stats, name='stats'),
    url(r'^chain$', views.chain_crawler, name='chain_crawler'),
    url(r'^createChain$', views.create_chain_crawler, name='createChain'),
    url(r'^error$', views.error, name='error'),
    url(r'^(?P<username>\w+)$', views.overview, name='overview'),
    url(r'^(?P<username>\w+)/(?P<crawlerName>\w+)$', views.crawler, name='crawler'),
)