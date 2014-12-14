import subprocess
from subprocess import PIPE
from django.shortcuts import render, redirect
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
    username = 'jayden'
    crawlers = Crawler.objects(owner='jayden')
    names = []
    for crawler in crawlers:
        names.append(crawler.crawlerName)
    request.session['crawlers'] = names
    return redirect('/' + username)

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
def overview(request, username):
    username = request.session.get('username');
    if username:
        print 'authenticated'
        crawlers = request.session.get('crawlers')
        # currently set to the page that i want to develop
        #return redirect('/create')
        return render(request, 'overview.html', {'username': username, 'crawlers': crawlers})
    else:
        print 'not auth'
        return render(request, 'index.html')

####
# Crawler profile page
####   
def monitor(request, username=None, crawlerName=None):
    username = request.session.get('username');
    if username:
        crawlers = request.session.get('crawlers')
        c = Crawler.objects.get(crawlerName=crawlerName)
        return render(request, 'monitor.html', {'username': username, 'crawlers': crawlers, 'crawler': c})
    
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
    
def updateCrawler(request):
    return

def deleteCrawler(request):
    return

####
# To start the crawler
#### 
def startCrawl(request, crawler):  
    if request.method == 'POST':  
        username = request.session.get('username') 
        if username:
            seeds = []
            crawlerName = request.POST['crawlerName']
            seeds.append(request.POST['crawlerSeeds'])
            try:
                crawler = Crawler(crawlerName=crawlerName, crawlerSeeds=seeds).save()
            except:
                print 'Not Created'    
        return render(request, 'monitor.html', {'crawler': crawler})

    return HttpResponse("Crawl failed")
    
####
# To stop the specific crawler
####       
def stopCrawl(request, crawler):
    if request.method == 'POST':
        
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

####
# to stop the crawler
####  
def stopCrawler(addr):
    try: 
        jsonrpc_client_call("http://" + addr + "/crawler/engine", 'close_spider', 'focras')
    except:
        print 'stopped'
