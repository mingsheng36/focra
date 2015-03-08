FOCRA
=====
**A Visual Cloud based Web Crawler** 
built using Django 1.7, MongoDB 2.6.5 and Scrapy 0.24.4

- Focra Demo ([http://focra-mingsheng36.rhcloud.com/](http://focra-mingsheng36.rhcloud.com/))

![alt text](https://github.com/mingsheng36/Focra/blob/master/docs/3.png "Demo")

##Features
- [x] Visually create your own XPath template
- [x] Toggle CSS and JavaScript on and off
- [x] Pagination Crawl
- [x] Chain Crawler (created from sublinks from initial crawler)
- [x] Pause/Resume Crawl
- [x] Show Hierarchy of Crawlers (how they are chained) 
- [x] View Data in Pages
- [x] User Accounts
- [ ] Improve on algorithms (Aggregation + Alignment)
- [ ] Export Data to Excel / CSV / JSON URL
- [ ] Schedule Crawl Frequency
- [ ] Crawl JavaScript Pages (Get from XHR request)
- [ ] Appending of Data (Latest data appending)
- [ ] Modify Field Names, Column Position and Template of the Crawler
- [ ] Change Database architecture (Not scalable as it uses one collection per crawler)
- [ ] Monitor Performance of Crawler
- [ ] Django Push Events (currently using poll)

###Things to Note
- The demo is a prototype for this project.
- Internet Explorer not supported.
- There is a download delay of 2 seconds to avoid affecting other servers.
