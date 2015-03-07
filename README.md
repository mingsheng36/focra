FOCRA
=====
**A Visual, Distributed and Cloud based Web Crawler** 
built with Django 1.7, Mongodb 2.6.5, Scrapy 0.24.4

![alt text](https://github.com/mingsheng36/Focra/blob/master/docs/3.png "Demo")

##Pre-requisites
- [Python 2.7](https://www.python.org/downloads/)
- [Pip](https://pip.pypa.io/en/latest/installing.html)
- [MongoDB](http://docs.mongodb.org/manual/installation/) 

##Instructions to deploy
1. Clone this repository or downlaod as zip
2. Command prompt >> cd to the cloned/downloaded directory 
3. Command prompt >> pip install -r requirements.txt
4. Create two database, 'FocraDB' and 'CrawlerDB' in your MongoDB using default host:port (127.0.0.1:27017)
5. Start MongoDB, command prompt >> mongod
6. Make sure you add this directory to your [PYTHONPATH](http://stackoverflow.com/a/4855685)
7. Command prompt >> python manage.py runserver
8. Go to [localhost:8000](http://localhost:8000) and start crawling!

##Features
- [x] Visually create your own XPath template
- [x] Toggle CSS and JavaScript on and off
- [x] Crawl Pagination
- [x] Baby Crawler (created from sublinks of Crawler)
- [x] Pause/Resume Crawl
- [x] Show Hierarchy of Crawlers (how they are related) 
- [x] Pause/Resume crawlers
- [x] View Data Pagination
- [ ] User Login/Logout/Registration
- [ ] Improve on algorithms (aggregation + alignment)
- [ ] Export Data to Excel / CSV / JSON URL
- [ ] Schedule Crawl Frequency
- [ ] Crawl JavaScript Pages
- [ ] Modify fields names, column position and template of the Crawler
- [ ] Change Database architecture (Not scalable as it uses one collection per crawler)
- [ ] Monitor Performance of Crawler
- [ ] Django Push Events (currently using poll)

###Things to Note
- This is not tested nor prettified, just a prototype for now.
- Internet Explorer not supported!
- There is a download delay of 2 seconds (you can change it in forbot/settings.py > DOWNLOAD_DELAY)
