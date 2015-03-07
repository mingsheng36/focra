FOCRA
=====
**A Visual, Distributed and Cloud based Web Crawler** 
built with Django 1.7, Mongodb 2.6.5, Scrapy 0.24.4

- Demo ([http://focra-mingsheng36.rhcloud.com/](http://focra-mingsheng36.rhcloud.com/))

![alt text](https://github.com/mingsheng36/Focra/blob/master/docs/3.png "Demo")

##Pre-requisites
- [Python 2.7](https://www.python.org/downloads/)
- [Pip](https://pip.pypa.io/en/latest/installing.html)
- [MongoDB](http://docs.mongodb.org/manual/installation/) 

##Features
- [x] Visually create your own XPath template
- [x] Toggle CSS and JavaScript on and off
- [x] Crawl Pagination
- [x] Baby Crawler (created from sublinks of Crawler)
- [x] Pause/Resume Crawl
- [x] Show Hierarchy of Crawlers (how they are related) 
- [x] Pause/Resume crawlers
- [x] View Data Pagination
- [x] User Login/Logout/Registration
- [ ] Improve on algorithms (aggregation + alignment)
- [ ] Export Data to Excel / CSV / JSON URL
- [ ] Schedule Crawl Frequency
- [ ] Crawl JavaScript Pages
- [ ] Appending of Data (Latest data appending)
- [ ] Modify fields names, column position and template of the Crawler
- [ ] Change Database architecture (Not scalable as it uses one collection per crawler)
- [ ] Monitor Performance of Crawler
- [ ] Django Push Events (currently using poll)

###Things to Note
- This is not tested nor prettified, just a prototype for now.
- Internet Explorer not supported!
- There is a download delay of 2 seconds (you can change it in forbot/settings.py > DOWNLOAD_DELAY)
