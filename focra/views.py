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
from bs4 import BeautifulSoup
from django.utils.safestring import mark_safe
from urlparse import urljoin
import urllib2
from collections import OrderedDict

# limit the total number of concurrent users
client = MongoClient('localhost', 27017,  max_pool_size=1000)
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
            try:
                crawlers = request.session.get('crawlers')
                crawler = Crawler.objects.get(crawlerName=crawlerName)
                request.session['crawlerName'] = crawler.crawlerName
                request.session['crawlerAddr'] = crawler.crawlerAddr
                request.session['crawlerSeeds'] = crawler.crawlerSeeds
                request.session['crawlerTemplate']= crawler.crawlerTemplate
                request.session['crawlerPager'] = crawler.crawlerPager
                request.session['crawlerStatus'] = crawler.crawlerStatus
                crawler.rows_inserted = db[crawlerName].count()
                if crawler.time_executed is None:
                    crawler.time_executed = "0"
                if crawler.crawled_pages is None:
                    crawler.crawled_pages = "0"
                # Retrieve and convert template into an ordered dict
                ordered_template_field = json.loads(crawler.crawlerTemplate, object_pairs_hook=collections.OrderedDict)
                # Determine which  one are links
                fields_w_link = []
                for key, value in ordered_template_field.items():
                    if re.sub("[^a-z]", "", value.split('/')[-1]) == 'a':
                        fields_w_link.append(key)
    
                return render(request, 'crawler.html', {'username': username, 
                                                        'crawlers': crawlers, 
                                                        'crawler': crawler, 
                                                        'ordered_template_field': ordered_template_field, 
                                                        'fields_w_link': fields_w_link})
            except Exception as err:
                print err
    return redirect('/')

def remove_duplicates_keys(ordered_pairs):
    d = OrderedDict()
    c = 1
    for k, v in ordered_pairs:
        # removes special chars and spaces
        k = re.sub('[^A-Za-z0-9]+', '', k)[:20]
        if not k:
            k = 'blank'
        if k in d:
            k = k+str(c)
            c += 1
            d[k] = v
        else:
            d[k] = v
    return d

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
                crawlerName = re.sub('[^A-Za-z0-9]+', '', request.POST['crawlerName']).lower()[:30]
                if not crawlerName:
                    crawlerName = 'blank'
                crawlerSeeds = request.POST['crawlerSeeds'].split('\r\n')
                crawlerTemplate = json.dumps(json.loads(request.POST['crawlerTemplate'], object_pairs_hook=remove_duplicates_keys))
                crawlerPager = request.POST['crawlerPager']
                crawlerStatus='running'
                crawlerAddr = runCrawler(crawlerName, crawlerSeeds, crawlerTemplate, crawlerPager, 'start')
                Crawler(crawlerName=crawlerName,
                        crawlerSeeds=crawlerSeeds,
                        crawlerAddr=crawlerAddr,
                        crawlerStatus=crawlerStatus,
                        crawlerPager=crawlerPager,
                        crawlerOwner=username,
                        crawlerTemplate=crawlerTemplate,
                        crawlerDateTime=datetime.now()).save()
                request.session['crawlers'] = crawlers + [crawlerName]
                return redirect('/' + username + '/' + crawlerName)
            except Exception as err:
                print err
    return redirect('/')
 
'''
Update current crawler in session
'''
def updateCrawler(request):
    return None
        
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
            db[crawlerName].drop()    
            return redirect('/' + username)
        except Exception as err:
            print err
    return redirect('/')

'''
Create Baby Crawler
'''
def baby(request, field=None):
    username = request.session.get('username')
    crawlers = request.session.get('crawlers')
    crawlerParent = request.session['crawlerName']
    if request.method == 'GET':
        try:
            cursor = db[crawlerParent].find({field:{'$ne':'null'}}, {field: 1}).limit(5)
            for link in cursor:
                if link.get(field):
                    soup = BeautifulSoup(link.get(field))
                    tag = soup.a
                    extracted_link = tag['href']
                    break
            return render(request, 'baby.html', {'username': username, 'crawlers': crawlers, 'extracted_link': extracted_link, 'field_link_name': field})        
        except Exception as err:
            print err
    elif request.method == 'POST':
        try:
            crawlerName = re.sub('[^A-Za-z0-9]+', '', request.POST['crawlerName']).lower()[:30]
            if not crawlerName:
                    crawlerName = 'blank'
            crawlerTemplate = json.dumps(json.loads(request.POST['crawlerTemplate'], object_pairs_hook=remove_duplicates_keys))
            crawlerPager = request.POST['crawlerPager']
            crawlerSeeds = [field, crawlerParent]
            crawlerStatus = 'running'
            crawlerAddr = runCrawler(crawlerName, crawlerSeeds, crawlerTemplate, crawlerPager, 'start')
            Crawler(crawlerName=crawlerName, 
                    crawlerSeeds=crawlerSeeds,
                    crawlerAddr=crawlerAddr, 
                    crawlerStatus=crawlerStatus,
                    crawlerPager=crawlerPager,
                    crawlerOwner=username,
                    crawlerTemplate=crawlerTemplate,
                    crawlerParent=crawlerParent,
                    crawlerDateTime=datetime.now()).save()
            # update parent crawler
            crawler = Crawler.objects.get(crawlerName=crawlerParent)
            crawler.crawlerBaby = crawlerName
            crawler.save()
        except Exception as err:
            print err
        request.session['crawlers'] = crawlers + [crawlerName]
        return redirect('/' + username + '/' + crawlerName)
'''
Handle start crawler requests
'''
def startCrawl(request):  
    if request.method == 'POST':  
        try:
            crawlerName = request.session.get('crawlerName')
            crawlerSeeds = request.session.get('crawlerSeeds')
            crawlerTemplate = request.session.get('crawlerTemplate')
            crawlerPager = request.session.get('crawlerPager')
            crawlerAddr = request.session.get('crawlerAddr')
            crawlerStatus = request.session.get('crawlerStatus')
            if db[crawlerName]:
                db[crawlerName].drop()
            if crawlerAddr == '' and crawlerStatus != 'running':
                crawlerAddr = runCrawler(crawlerName, crawlerSeeds, crawlerTemplate, crawlerPager, 'start')
                Crawler.objects(crawlerName=crawlerName).update_one(set__crawlerStatus='running',
                                                                    set__crawlerAddr=crawlerAddr)
                request.session['crawlerAddr'] = crawlerAddr
                request.session['crawlerStatus'] = 'running'
                print crawlerName + ' - Running at ' + crawlerAddr
                return HttpResponse(crawlerName + ' is running')
            else:
                return HttpResponse(crawlerName + ' is already running')
        except Exception as err:
            print err
    else:
        return HttpResponse("Crawl failed")
    
'''
Handle stop crawler requests
'''      
def stopCrawl(request):
    if request.method == 'POST':
        try:
            crawlerName = request.session.get('crawlerName')
            crawlerAddr = request.session.get('crawlerAddr')
            crawlerStatus = request.session.get('crawlerStatus')
            if crawlerStatus == 'running':
                print crawlerName + ' - Stopping at ' + request.session.get('crawlerAddr')
                stopCrawler(crawlerAddr)
                Crawler.objects(crawlerName=crawlerName).update_one(set__crawlerStatus='stopped',
                                                                    set__crawlerAddr='')
                request.session['crawlerAddr'] = ''
                request.session['crawlerStatus'] = 'stopped'
                return HttpResponse(crawlerName + ' has been stopped')
            else:
                return HttpResponse(crawlerName + ' is not running!')
        except Exception as err:
            print err
    else:
        return HttpResponse("Stop failed")
 
'''
Handle pause crawler requests
'''      
def pauseCrawl(request):
    if request.method == 'POST':
        try:
            crawlerName = request.session.get('crawlerName')
            crawlerAddr = request.session.get('crawlerAddr')
            crawlerStatus = request.session.get('crawlerStatus')
            if crawlerAddr != '' and crawlerStatus == 'running':
                print crawlerName + ' - Pausing at ' + request.session.get('crawlerAddr')
                stopCrawler(request.session.get('crawlerAddr'))
                Crawler.objects(crawlerName=crawlerName).update_one(set__crawlerStatus='paused', set__crawlerAddr='')
                request.session['crawlerAddr'] = ''
                request.session['crawlerStatus'] = 'paused'
                return HttpResponse(crawlerName + ' has been paused')
            else:
                return HttpResponse(crawlerName + ' is not running!')
        except Exception as err:
            print err
    else:
        return HttpResponse("Pause failed")

'''
Handle resume crawler requests
'''      
def resumeCrawl(request):
    if request.method == 'POST':  
        try:
            crawlerName = request.session.get('crawlerName')
            crawlerSeeds = request.session.get('crawlerSeeds')
            crawlerTemplate = request.session.get('crawlerTemplate')
            crawlerPager = request.session.get('crawlerPager')
            crawlerAddr = request.session.get('crawlerAddr')
            crawlerStatus = request.session.get('crawlerStatus')
            if crawlerAddr == '' and crawlerStatus == 'paused':
                crawlerAddr = runCrawler(crawlerName, crawlerSeeds, crawlerTemplate, crawlerPager, 'resume')
                Crawler.objects(crawlerName=crawlerName).update_one(set__crawlerStatus='running', set__crawlerAddr=crawlerAddr)
                request.session['crawlerAddr'] = crawlerAddr
                request.session['crawlerStatus'] = 'running'
                return HttpResponse(crawlerName + ' has been resumed')
            else:
                return HttpResponse(crawlerName + ' was not paused!')
        except Exception as err:
            print err
    else:
        return HttpResponse("Resume failed")

'''
Returns crawler running address
Starting the crawler through cmdline in local machine
Needs to be changed to start through HTTP call for scalability
'''  
def runCrawler(name, seeds, template, pager, runtype, pager_link=None):
    try:
        commands = ["scrapy", "crawl", "focras", 
                    "-a", "cname=" + name.strip(), 
                    "-a", "seeds=" + ','.join(seeds).strip(),
                    "-a", "template=" + template.strip(), 
                    "-a", "pager=" + pager.encode('ascii', 'xmlcharrefreplace'),
                    "-a", "runtype=" + runtype.strip()]
        crawlerProcess = subprocess.Popen(commands, stderr=PIPE)
        while True:
            line = crawlerProcess.stderr.readline()
            # to view the process output, uncomment below 
            # print line
            crawlerAddr = re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[0-9]{1,5}', line)
            if crawlerAddr:
                print name + ' running at '+ ''.join(crawlerAddr)
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
    except Exception:
        pass

'''
Fetch seed URl and do HTML pre-processing
'''
def fetch(request):
    if request.method == 'GET':
        try:  
            url = request.GET['url']
            if not url.startswith("http"):
                return HttpResponse("format")
            js = request.GET['js']
            css = request.GET['css']
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
                
            soup = BeautifulSoup(cleaned_resp)
            
            # fix page being redirected
            for tag in soup.find_all('span', onclick=True):
                tag['onclick'] = ""
                
            # patch the css url so it will load from the server
            for tag in soup.find_all('link', href=True):
                if css == 'true':
                    if 'http' not in tag['href']:
                        tag['href'] = urljoin(url, tag['href'])
                else:
                    tag.decompose()
            
            # patch image url so it will load from the server
            for tag in soup.find_all('img', src=True):
                if 'http' not in tag['src']:
                    tag['src'] = urljoin(url, tag['src'])
            
            # load external script for web page to load properly
            # so users are more familiar with the interface
            for tag in soup.find_all('script', src=True):
                if js == 'true':
                    tag.decompose()
                else:
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
            
            # remove all the tbody before generating the html source
            # iframe at create.html will still generate a general tbody tag
            for tag in soup.find_all('tbody'):
                tag.unwrap()
            
            # inject focra.css into response
            css_tag = soup.new_tag("link", rel="stylesheet", type="text/css", href='http://localhost:8000/static/css/focra.css')
            soup.head.append(css_tag)

            return HttpResponse(mark_safe(soup.prettify(encoding='ascii')))
        except urllib2.HTTPError as err:
            return HttpResponse(str(err.code))
        except ValueError:
            return HttpResponse("format")
        except Exception as err:
            return HttpResponse("format")
            

'''
Display Crawler data from CrawlerDB
'''
def data(request):
    try: 
        crawlerName = request.session.get('crawlerName')
        collection = db[crawlerName]
        return HttpResponse(dumps(collection.find()))
    except Exception as err:
        print err

'''
Validate Crawler unique names
'''
def check_name(request):
    if request.method == 'GET':
        try:
            if request.GET['crawlerName']:
                crawlerName = re.sub('[^A-Za-z0-9]+', '', request.GET['crawlerName']).lower()[:30]
                c = Crawler.objects(crawlerName=crawlerName)
                if c:
                    return HttpResponse("invalid")
                else:
                    return HttpResponse("valid")
            else:
                return HttpResponse("invalid")
        except Exception as err:
            print err