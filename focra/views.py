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
    username = 'mingsheng'
    request.session['username'] = username
    return redirect('/' + username)
#     if request.method == 'GET':      
#         return render(request, 'index.html')   
#     elif request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         request.session['username'] = username
#         newUser = User(username=username, password=password).save()
#         print newUser.username
#         return redirect('/' + username)
#     else: 
#         return render(request, 'index.html')

'''
Home page to authenticated usernames
'''   
def overview(request, username):
    #dev purpose
    request.session['username'] = username
    username = request.session.get('username');
    if username:
        if request.method == 'GET':
            
                print 'authenticated'
                crawlers = Crawler.objects(crawlerOwner=username)
                return render(request, 'overview.html', {'username': username, 'crawlers': crawlers})
    print 'not authorised'
    return redirect('/')
    
'''
Crawler page to manage crawler
'''   
def crawler(request, username=None, crawlerName=None):
    username = request.session.get('username');
    if username:
        if request.method == 'GET':
            try:
                chain_crawler = None
                chains = None
                crawlers = Crawler.objects(crawlerOwner=username)
                crawler = Crawler.objects.get(crawlerName=crawlerName)
                if len(crawler.crawlerSeeds) > 1:
                    # tell the UI this is a chain crawler
                    chain_crawler = "request_url"
                    chains = [crawler.crawlerSeeds[1]]
                    c = crawler.crawlerSeeds[1]
                    while(True):
                        try:
                            c = Crawler.objects.get(crawlerName=c).crawlerParent
                        except Exception as err:
                            break
                        if c is not None:
                            chains.append(c)
                        else:
                            break
                crawler.rows_inserted = db[crawlerName].count()
                if crawler.rows_inserted is None:
                    crawler.rows_inserted = "0"
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
                                                        'fields_w_link': fields_w_link,
                                                        'chain_crawler': chain_crawler,
                                                        'chains': chains })
            except Exception as err:
                print err
    return redirect('/')

def remove_duplicates_keys(ordered_pairs):
    d = OrderedDict()
    c = 1
    for k, v in ordered_pairs:
        # removes special chars and spaces
        k = re.sub('[^A-Za-z0-9]+', '_', k)[:20]
        if not k:
            k = 'blank'
        if k == 'request_url':
            k = 'request_url1' 
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
    if username:
        if request.method == 'GET':
            crawlers = Crawler.objects(crawlerOwner=username)
            return render(request, 'create.html', {'username': username, 'crawlers': crawlers})
        if request.method == 'POST':   
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
                return redirect('/' + username + '/' + crawlerName)
            except Exception as err:
                print err
    else:
        return redirect('/')
 
'''
Update current crawler
'''
def updateCrawler(request):
    return None
        
'''
Delete current crawler
'''
def deleteCrawler(request):
    username = request.session.get('username')
    if username:
        if request.method == 'POST':  
            try:
                crawlerName = request.POST['crawlerName']
                Crawler.objects(crawlerName=crawlerName).delete()
                db[crawlerName].drop()    
                return redirect('/' + username)
            except Exception as err:
                print err
    else:
        return redirect('/')

'''
Create Chain Crawler
'''
def chain_crawler(request):
    username = request.session.get('username')
    if username:
        if request.method == 'GET':
            try:
                crawlerParent = request.GET['crawlerName']
                field = request.GET['field']
                cursor = db[crawlerParent].find({field:{'$ne':'null'}}, {field: 1}, limit=50)
                return HttpResponse(dumps(cursor))
            except Exception as err:
                print err
        elif request.method == 'POST':
            try:
                crawlers = Crawler.objects(crawlerOwner=username)
                return render(request, 'chain.html', {'username': username, 
                                                      'crawlers': crawlers, 
                                                      'chainJS': request.POST['chainJS'], 
                                                      'chainCSS': request.POST['chainCSS'],
                                                      'chainURL': request.POST['chainSelectedURL'],
                                                      'chainField': request.POST['chainField'],
                                                      'chainParent': request.POST['chainParent']})
            except Exception as err:
                print err
    else:
        return redirect('/')

def create_chain_crawler(request):
    username = request.session.get('username')
    if username:
        if request.method == 'POST':
            try:
                crawlerName = re.sub('[^A-Za-z0-9]+', '', request.POST['crawlerName']).lower()[:30]
                if not crawlerName:
                        crawlerName = 'blank'
                crawlerTemplate = json.dumps(json.loads(request.POST['crawlerTemplate'], object_pairs_hook=remove_duplicates_keys))
                crawlerPager = request.POST['crawlerPager']
                crawlerParent = request.POST['crawlerParent']
                print crawlerParent + " asdasdasdasd"
                crawlerSeeds = [request.POST['chainField'], crawlerParent]
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
                Crawler.objects(crawlerName=crawlerParent).update_one(set__crawlerBaby=crawlerName)
                return redirect('/' + username + '/' + crawlerName)
            except Exception as err:
                print err
    else:
        return redirect('/')

'''
Handle start crawler requests
'''
def startCrawl(request):
    username = request.session.get('username')
    if username:
        if request.method == 'POST':  
            try:
                crawlerName = request.POST['crawlerName']
                c = Crawler.objects.get(crawlerName=crawlerName)
                if db[crawlerName]:
                    db[crawlerName].drop()
                if c.crawlerAddr == '' and c.crawlerStatus != 'running':  
                    if len(c.crawlerSeeds) > 1:
                        if Crawler.objects.with_id(c.crawlerSeeds[1]) is None:
                            return HttpResponse("ParentDontExists")
                    crawlerAddr = runCrawler(crawlerName, c.crawlerSeeds, c.crawlerTemplate, c.crawlerPager, 'start')
                    Crawler.objects(crawlerName=crawlerName).update_one(set__crawlerStatus='running',
                                                                        set__crawlerAddr=crawlerAddr)
                    print crawlerName + ' - Running at ' + crawlerAddr
                    return HttpResponse(crawlerName + ' is running')
                           
                else:
                    return HttpResponse(crawlerName + ' is already running')
            except Exception as err:
                print err
    return HttpResponse("Crawl failed")

    
'''
Handle stop crawler requests
'''      
def stopCrawl(request):
    username = request.session.get('username')
    if username:
        if request.method == 'POST':
            try:
                crawlerName = request.POST['crawlerName']
                c = Crawler.objects.get(crawlerName=crawlerName)
                if c.crawlerStatus == 'running':
                    print crawlerName + ' - Stopping at ' + c.crawlerAddr
                    stopCrawler(c.crawlerAddr)
                    Crawler.objects(crawlerName=crawlerName).update_one(set__crawlerStatus='stopped',
                                                                        set__crawlerAddr='')
                    return HttpResponse(crawlerName + ' has been stopped')
                else:
                    return HttpResponse(crawlerName + ' is not running!')
            except Exception as err:
                print err
    return HttpResponse("Stop failed")
 
'''
Handle pause crawler requests
'''      
def pauseCrawl(request):
    username = request.session.get('username')
    if username:
        if request.method == 'POST':
            try:
                crawlerName = request.POST['crawlerName']
                c = Crawler.objects.get(crawlerName=crawlerName)
                print c.crawlerAddr + c.crawlerStatus
                if c.crawlerAddr != '' and c.crawlerStatus == 'running':
                    print crawlerName + ' - Pausing at ' + c.crawlerAddr
                    stopCrawler(c.crawlerAddr)
                    Crawler.objects(crawlerName=crawlerName).update_one(set__crawlerStatus='paused', set__crawlerAddr='')
                    return HttpResponse(crawlerName + ' has been paused')
                else:
                    return HttpResponse(crawlerName + ' is not running!')
            except Exception as err:
                print err
    return HttpResponse("Pause failed")

'''
Handle resume crawler requests
'''      
def resumeCrawl(request):
    username = request.session.get('username')
    if username:
        if request.method == 'POST':  
            try:
                crawlerName = request.POST['crawlerName']            
                c = Crawler.objects.get(crawlerName=crawlerName)
                if c.crawlerAddr == '' and c.crawlerStatus == 'paused':
                    if len(c.crawlerSeeds) > 1:
                        if Crawler.objects.with_id(c.crawlerSeeds[1]) is None:
                            return HttpResponse("ParentDontExists")
                    crawlerAddr = runCrawler(crawlerName, c.crawlerSeeds, c.crawlerTemplate, c.crawlerPager, 'resume')
                    Crawler.objects(crawlerName=crawlerName).update_one(set__crawlerStatus='running', set__crawlerAddr=crawlerAddr)
                    return HttpResponse(crawlerName + ' has been resumed')
                else:
                    return HttpResponse(crawlerName + ' was not paused!')
            except Exception as err:
                print err
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
    username = request.session.get('username')
    if username:
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
    return HttpResponse("")
            

'''
Display Crawler data from CrawlerDB
'''
def data(request):
    username = request.session.get('username')
    if username:
        if request.method == 'GET':
            try: 
                crawlerName = request.GET['crawlerName']
                start = request.GET['start']
                row_limit = request.GET['rowLimit']
                return HttpResponse(str(db[crawlerName].count()) + "," + dumps(db[crawlerName].find(skip=int(start),
                                                                                                    limit=int(row_limit))))
            except Exception as err:
                print err
    return HttpResponse("")

'''
Validate Crawler unique names
'''
def check_name(request):
    username = request.session.get('username')
    if username:
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
    return HttpResponse("")
            
def stats(request):
    username = request.session.get('username')
    if username:
        if request.method == 'GET':
            try:
                if request.GET['crawlerName']:
                    crawlerName = request.GET['crawlerName']
                    
                    c = Crawler.objects.get(crawlerName=crawlerName)      
                    return HttpResponse(str(c.crawlerStatus) + "," +
                                        str(c.crawled_pages) + "," +
                                        str(db[crawlerName].count()) + "," +
                                        str(c.time_executed))
            except Exception as err:
                print err
    return HttpResponse("");