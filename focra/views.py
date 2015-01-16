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
    '''
    Development purpose, login as jayden
    '''
    username = 'Jayden'
    request.session['username'] = username
    crawlers = Crawler.objects(crawlerOwner=username)
    names = []
    for crawler in crawlers:
        names.append(crawler.crawlerName)
    request.session['crawlers'] = names
    return redirect('/' + username)
    '''
    if request.method == 'GET':      
        return render(request, 'index.html')   
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        request.session['username'] = username
        newUser = User(username=username, password=password).save()
        print newUser.username
        return home(request)
    else: 
        return render(request, 'index.html')
    '''

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
            crawlerName = request.POST['crawlerName']
            crawlerSeeds=request.POST['crawlerSeeds'].split('\r\n')
            crawlerTemplate=request.POST['crawlerTemplate']
            try:
                crawlerAddr = runCrawler(crawlerName, crawlerSeeds, crawlerTemplate)
                Crawler(crawlerName=crawlerName, 
                        crawlerSeeds=crawlerSeeds, 
                        crawlerAddr=crawlerAddr, 
                        crawlerStatus='running', 
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
    return

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
            #return HttpResponse(crawlerName + " has been deleted.")
            #return render(request, 'overview.html', {'username': username, 'crawlers': crawlers})
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
        try:
            crawlerAddr = runCrawler(crawlerName, crawlerSeeds, crawlerTemplate)
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
def runCrawler(name, seeds, template):
    commands = ["scrapy", "crawl", "focras", "-a", "name=" + name, "-a", "seeds=" + ','.join(seeds), "-a", "template=" + template]
    crawlerProcess = subprocess.Popen(commands, stderr=PIPE)    
    while True:
        line = crawlerProcess.stderr.readline()
        crawlerAddr = re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[0-9]{1,5}', line)
        if crawlerAddr:
            print ''.join(crawlerAddr)
            break;
        if line == '' and crawlerProcess.poll() != None:
            break;
    return ''.join(crawlerAddr)

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

            '''
            JavaScript support but very slow
            '''
#             import os
#             p = subprocess.Popen(["python", os.path.dirname(os.path.dirname(__file__)) +'/scripts/test.py', url], stdout=PIPE)  
#             cleaned = ''
#             while True:
#                 res = p.stdout.readline()
#                      
#                 if res == '' and p.poll() != None:
#                     break
#                 a = re.findall('url\((.*?)\)', res)   
#                 if a:
#                     for link in a:           
#                         if 'http' not in link:
#                             link = link.replace("'","")
#                             link = link.replace('"',"")
#                             res = re.sub("url\((.*?)\)", 'url(' + str(urljoin(parsed_url.scheme + "://" + parsed_url.netloc + "/", ''.join(link))) + ')' , res)
#                             print res
#                 cleaned = cleaned + str(res)
            
            '''
            No JavaScript support, fast
            '''
            import urllib2
            req = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            r = urllib2.urlopen(req)
            cleaned = ''
            for line in r:
                a = re.findall('url\((.*?)\)', line)

                if a:
                    for link in a:  
                        if 'http' not in link:
                            link = link.replace("'","")
                            link = link.replace('"',"")
                            line = re.sub("url\((.*?)\)"
                                          , 'url(' + str(url) + ''.join(link) + ')' 
                                          , line) 
                    
                cleaned = cleaned + line

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(cleaned)
            
            for tag in soup.find_all('a', href=True):
                tag['href'] = "javascript:void(0)"
                tag['rel'] = "javascript:void(0)"
                tag['onclick'] = "javascript:void(0)"
                tag['target'] = "javascript:void(0)"
                
            for tag in soup.find_all('link', href=True):
                if 'http' not in tag['href']:
                    tag['href'] = urljoin(url, tag['href'])
                    
            for tag in soup.find_all('img', src=True):
                if 'http' not in tag['src']:
                    tag['src'] = urljoin(url, tag['src'])
                    
            for tag in soup.find_all('script', src=True):
                if 'http' not in tag['src']:
                    tag['src'] = urljoin(url, tag['src'])
                               
            for tag in soup.find_all('iframe', src=True):
                tag['src'] = ""
            
#             for tag in soup.find_all('script', async=True):
#                 tag.decompose()
            '''
            Can implement injection of javascript into the HTML response to 'clean' the response
            '''
            '''
            Inject Focra CSS into the HTML response
            '''
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