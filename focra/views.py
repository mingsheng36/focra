import subprocess
from subprocess import PIPE
from django.shortcuts import render
#import threading
from django.http import HttpResponse
from scrapy.utils.jsonrpc import jsonrpc_client_call
import re
from models import Crawler

####
# welcome page and sign up page
#### 
def index(request):
    # DEVELOPMENT PURPOSE
    request.session['username'] = 'jayden'
    crawlers = Crawler.objects(owner='jayden')
    names = []
    for crawler in crawlers:
        names.append(crawler.crawlerName)
    request.session['crawlers'] = names 
    return overview(request)

    #  FOR PRODUCTION USE
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

####
# display home page to authenticated usernames
####   
def overview(request):
    username = request.session.get('username');
    if username:
        print 'authenticated'
        # currently set to the page that i want to develop
        return createCrawler(request)
    else:
        print 'not auth'
        return render(request, 'index.html')

####
# To create crawler
####
def createCrawler(request):
    
    if request.method == 'GET':
        username = request.session.get('username')
        crawlers = request.session.get('crawlers')
        if username:
            return render(request, 'create.html', {'username': username, 'crawlers': crawlers})
            
    if request.method == 'POST':   
        username = request.session.get('username')
        if username:
            seeds = []
            crawlerName = request.POST['crawlerName']
            seeds.append(request.POST['crawlerSeeds'])
            try:
                addr = runCrawler(seeds);
                crawler = Crawler(crawlerName=crawlerName, crawlerSeeds=seeds, crawlerPort=''.join(addr), crawlerStatus='running', owner=username).save()
                return monitor(request, crawler=crawler)
            except:
                print 'error'
        
    return render(request, 'index.html')

def monitor(request, crawler=None):
    crawlers = request.session.get('crawlers')
    if crawler:
        return render(request, 'monitor.html', {'crawler': crawler, 'crawlers': crawlers})
    
def updateCrawler(request):
    return

def deleteCrawler(request):
    return

####
# To start the crawler
#### 
def startCrawl(request):  

#     if request.method == 'POST':  
#         username = request.session.get('username') 
#         if username:
#             seeds = []
#             crawlerName = request.POST['crawlerName']
#             seeds.append(request.POST['crawlerSeeds'])
#             try:
#                 crawler = Crawler(crawlerName=crawlerName, crawlerSeeds=seeds).save()
#             except:
#                 print 'Not Created'    
#         return render(request, 'monitor.html', {'crawler': crawler})

    return HttpResponse("Crawl failed")
    
####
# To stop the specific crawler
####       
def stopCrawl(request):
    if request.method == 'GET':
        try: 
            jsonrpc_client_call("http://localhost:6080/crawler/engine", 'close_spider', 'focras')
        except:
            print 'stopped'
        return HttpResponse("Crawl Stopped")
    return HttpResponse("Failed to stop")

####
# to run the crawler
####  
def runCrawler(seeds):
    commands = ["scrapy", "crawl", "focras", "-a", "seeds=" + ''.join(seeds)]
    scrapyProcess = subprocess.Popen(commands, stderr=PIPE)    
    while True:
        scrapyWebAddr = re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[0-9]{1,5}', scrapyProcess.stderr.readline())
        if scrapyWebAddr:
            print scrapyWebAddr
            break;
    return scrapyWebAddr
