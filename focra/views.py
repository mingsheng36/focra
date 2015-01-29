import subprocess, re
from subprocess import PIPE
from django.shortcuts import render, redirect
from django.http import HttpResponse
from scrapy.utils.jsonrpc import jsonrpc_client_call
from models import Crawler
import json, collections
from datetime import datetime
from bson.json_util import dumps
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client['CrawlerDB']

'''
welcome page and sign up page
''' 
def index(request):
    # Development purpose, login as Jayden
    username = 'Jayden'
    request.session['username'] = username
    crawlers = Crawler.objects(crawlerOwner=username)
    names = []
    for crawler in crawlers:
        names.append(crawler.crawlerName)
    request.session['crawlers'] = names
    return redirect('/' + username)
    
#     if request.method == 'GET':      
#         return render(request, 'index.html')   
#     elif request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         request.session['username'] = username
#         newUser = User(username=username, password=password).save()
#         print newUser.username
#         return home(request)
#     else: 
#         return render(request, 'index.html')
    

'''
Home page to authenticated usernames
'''   
def overview(request, username):
    if request.method == 'GET':
        username = request.session.get('username');
        if username:
            print 'authenticated'
            crawlers = request.session.get('crawlers')
            return render(request, 'overview.html', {'username': username, 'crawlers': crawlers})
        else:
            print 'not authorised'
            return redirect('/')

'''
Crawler page to manage crawler
'''   
def crawler(request, username=None, crawlerName=None):
    if request.method == 'GET':
        username = request.session.get('username');
        if username:
            crawlers = request.session.get('crawlers')
            crawler = Crawler.objects.get(crawlerName=crawlerName)
            request.session['crawlerName'] = crawler.crawlerName
            request.session['crawlerAddr'] = crawler.crawlerAddr
            request.session['crawlerSeeds'] = crawler.crawlerSeeds
            request.session['crawlerTemplate']= crawler.crawlerTemplate
            request.session['crawlerPager'] = crawler.crawlerPager
            # Retrieve and convert template into an ordered dict
            t = json.loads(crawler.crawlerTemplate, object_pairs_hook=collections.OrderedDict)
            return render(request, 'crawler.html', {'username': username, 'crawlers': crawlers, 'crawler': crawler, 't': t})
    
'''
Create a new crawler
'''
def createCrawler(request):
    username = request.session.get('username')
    crawlers = request.session.get('crawlers')
    if request.method == 'GET':
        if username:
            return render(request, 'create.html', {'username': username, 'crawlers': crawlers})
    if request.method == 'POST':   
        if username:
            try:
                crawlerName = request.POST['crawlerName']
                crawlerSeeds = request.POST['crawlerSeeds'].split('\r\n')
                crawlerTemplate = request.POST['crawlerTemplate']
                crawlerPager = request.POST['crawlerPager']
                crawlerAddr = runCrawler(crawlerName, crawlerSeeds, crawlerTemplate, crawlerPager)
                Crawler(crawlerName=crawlerName, 
                        crawlerSeeds=crawlerSeeds, 
                        crawlerAddr=crawlerAddr, 
                        crawlerStatus='running',
                        crawlerPager=crawlerPager,
                        crawlerOwner=username, 
                        crawlerTemplate=crawlerTemplate,
                        crawlerDateTime=datetime.now()).save()
            except Exception as err:
                print err
            request.session['crawlers'] = crawlers + [crawlerName]
            return redirect('/' + username + '/' + crawlerName)
        
    return redirect('/')
 
'''
Update current crawler in session
'''
def updateCrawler(request):
    return None

'''
Create Baby Crawler
'''
def baby(request):
    username = request.session.get('username')
    crawlers = request.session.get('crawlers')
    if request.method == 'GET':
        return render(request, 'baby.html', {'username': username, 'crawlers': crawlers})
        
'''
Delete current crawler in session
'''
def deleteCrawler(request):
    if request.method == 'POST':  
        try:
            username = request.session.get('username')
            crawlerName = request.session.get('crawlerName')
            stopCrawler(request.session.get('crawlerAddr'))
            Crawler.objects(crawlerName=crawlerName).delete()
            crawlers = request.session.get('crawlers')
            crawlers.remove(crawlerName)
            request.session['crawlers'] = crawlers
            collection = db[crawlerName]
            collection.drop()     
            return redirect('/' + username)
        except Exception as err:
            print err
    return

'''
Handle start crawler requests
'''
def startCrawl(request):  
    if request.method == 'POST':  
        crawlerName = request.session.get('crawlerName')
        crawlerSeeds = request.session.get('crawlerSeeds')
        crawlerTemplate = request.session.get('crawlerTemplate')
        crawlerPager = request.session.get('crawlerPager')
        try:
            crawlerAddr = runCrawler(crawlerName, crawlerSeeds, crawlerTemplate, crawlerPager)
            Crawler.objects(crawlerName=crawlerName).update_one(set__crawlerStatus='running', set__crawlerAddr=crawlerAddr)
            request.session['crawlerAddr'] = crawlerAddr
        except Exception as err:
            print err
        return HttpResponse(crawlerName + ' is running')
    else:
        return HttpResponse("Crawl failed")
        
    return redirect('/')
    
'''
Handle stop crawler requests
'''      
def stopCrawl(request):
    if request.method == 'POST':
        print 'stopping ' + request.session.get('crawlerAddr')
        try:
            crawlerName = request.session.get('crawlerName')
            stopCrawler(request.session.get('crawlerAddr'))
            Crawler.objects(crawlerName=crawlerName).update_one(set__crawlerStatus='stopped', set__crawlerAddr='')
        except Exception as err:
            print err
        return HttpResponse(crawlerName + ' has been stopped')
    else:
        return HttpResponse("Stop failed")
    return redirect('/')

'''
Starting the crawler through cmdline in local machine
Needs to be changed to start through HTTP call for scalability
'''  
def runCrawler(name, seeds, template, pager):
    try:
        commands = ["scrapy", "crawl", "focras", 
                    "-a", "name=" + name, 
                    "-a", "seeds=" + ','.join(seeds), 
                    "-a", "template=" + template, 
                    "-a", "pager=" + pager.encode('ascii', 'xmlcharrefreplace')]
        crawlerProcess = subprocess.Popen(commands, stderr=PIPE)
        while True:
            line = crawlerProcess.stderr.readline()
            # to view the process output 
            #print line
            crawlerAddr = re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[0-9]{1,5}', line)
            if crawlerAddr:
                print ''.join(crawlerAddr)
                crawlerProcess.stderr.close()
                break;
            if line == '' and crawlerProcess.poll() != None:
                break;
        return ''.join(crawlerAddr)
    except Exception as err:
        print err

'''
Stopping crawler through JSONRPC
'''  
def stopCrawler(addr):
    try: 
        jsonrpc_client_call("http://" + addr + "/crawler/engine", 'close_spider', 'focras')
    except:
        print 'Expected stop error, don\'t worry'

'''
Fetch seed URl and do HTML pre-processing
'''
def fetch(request):
    if request.method == 'GET':
        try: 
            from urlparse import urljoin
            url = request.GET['url']              
            # No JavaScript support, fast
            import urllib2
            req = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib2.urlopen(req)
            cleaned_resp = ''
            for line in resp:
                # fix for some forums templates, prevent popups
                line = line.replace('popupctrl', '')
                line = line.replace('popupmenu', '')
                a = re.findall('url\((.*?)\)', line)
                if a:
                    for link in a:  
                        if 'http' not in link:
                            link = link.replace("'","")
                            link = link.replace('"',"")
                            line = re.sub("url\((.*?)\)"
                                          , 'url(' + str(url) + ''.join(link) + ')' 
                                          , line) 
                    
                cleaned_resp = cleaned_resp + line

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(cleaned_resp)
            
            # patch the css url so it will load from the server
            for tag in soup.find_all('link', href=True):
                if 'http' not in tag['href']:
                    tag['href'] = urljoin(url, tag['href'])
            
            # patch image url so it will load from the server
            for tag in soup.find_all('img', src=True):
                if 'http' not in tag['src']:
                    tag['src'] = urljoin(url, tag['src'])
            
            # load external script for web page to load properly
            # so users are more familiar with the interface
            for tag in soup.find_all('script', src=True):
                if 'http' not in tag['src']:
                    tag['src'] = urljoin(url, tag['src'])

            # fix for some forums, disable in-line scripts that prevents page from loading
            # e.g http://www.kiasuparents.com/kiasu/forum/index.php
            for tag in soup.find_all('script', src=False):
                tag.decompose()

            # disable and remove all iframe to prevent errors
            for tag in soup.find_all('iframe', src=True):
                tag['src'] = ''
                tag['srcdoc'] = ''
  
            # inject focra.css into response
            css_tag = soup.new_tag("link", rel="stylesheet", type="text/css", href='http://localhost:8000/static/css/focra.css')
            soup.head.append(css_tag)
            
            from django.utils.safestring import mark_safe
            return HttpResponse(mark_safe(soup.prettify()))
    
        except Exception as err:
            print err

'''
Display Crawler data from CrawlerDB
'''
def data(request):
    try: 
        crawlerName = request.session.get('crawlerName')
        collection = db[crawlerName]
        return HttpResponse(dumps(collection.find()))
    except Exception as e:
        print e