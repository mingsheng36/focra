import subprocess
from subprocess import PIPE
from django.shortcuts import render, redirect
#import threading
from django.http import HttpResponse
from scrapy.utils.jsonrpc import jsonrpc_client_call
import re
from models import Crawler

'''
welcome page and sign up page
''' 
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

'''
display home page to authenticated usernames
'''   
def overview(request, username):
    if request.method == 'GET':
        username = request.session.get('username');
        if username:
            print 'authenticated'
            crawlers = request.session.get('crawlers')
            # currently set to the page that i want to develop
            #return redirect('/create')
            return render(request, 'overview.html', {'username': username, 'crawlers': crawlers})
        else:
            print 'not authorised'
            return redirect('/')

'''
Crawler profile page
'''   
def monitor(request, username=None, crawlerName=None):
    if request.method == 'GET':
        username = request.session.get('username');
        if username:
            crawlers = request.session.get('crawlers')
            crawler = Crawler.objects.get(crawlerName=crawlerName)
            request.session['crawlerName'] = crawler.crawlerName
            request.session['crawlerAddr'] = crawler.crawlerAddr
            request.session['crawlerSeeds'] = crawler.crawlerSeeds
            return render(request, 'monitor.html', {'username': username, 'crawlers': crawlers, 'crawler': crawler})
    
'''
To create crawler
'''
def createCrawler(request):
    username = request.session.get('username')
    crawlers = request.session.get('crawlers')
    if request.method == 'GET':
        if username:
            return render(request, 'create.html', {'username': username, 'crawlers': crawlers})
    if request.method == 'POST':   
        if username:
            seeds = []
            crawlerName = request.POST['crawlerName']
            seeds.append(request.POST['crawlerSeeds'])
            try:
                addr = runCrawler(seeds);
                Crawler(crawlerName=crawlerName, crawlerSeeds=seeds, crawlerAddr=''.join(addr), crawlerStatus='running', owner=username).save()
                request.session['crawlers'] = crawlers + [crawlerName]
                return redirect('/' + username + '/' + crawlerName)
            except:
                print 'error'
        
    return redirect('/')
    
def updateCrawler(request):
    return

def deleteCrawler(request):
    return

'''
To start the crawler
'''
def startCrawl(request):  
    if request.method == 'POST':  
        return HttpResponse("Crawl Started!")
    else:
        return HttpResponse("Crawl failed")
        
    return redirect('/')
    
'''
To stop the specific crawler
'''      
def stopCrawl(request):
    if request.method == 'POST':
        stopCrawler(request.session.get('crawlerAddr'))
        Crawler.objects(crawlerName=request.session.get('crawlerName')).update_one(crawlerStatus='stopped')
        return HttpResponse("Crawl Stopped")
    else:
        return HttpResponse("Stop failed")
    return redirect('/')

'''
to run the crawler
'''  
def runCrawler(seeds):
    commands = ["scrapy", "crawl", "focras", "-a", "seeds=" + ''.join(seeds)]
    scrapyProcess = subprocess.Popen(commands, stderr=PIPE)    
    while True:
        scrapyWebAddr = re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[0-9]{1,5}', scrapyProcess.stderr.readline())
        if scrapyWebAddr:
            print scrapyWebAddr
            break;
    return scrapyWebAddr

'''
to stop the crawler
'''  
def stopCrawler(addr):
    try: 
        jsonrpc_client_call("http://" + addr + "/crawler/engine", 'close_spider', 'focras')
    except:
        print 'stopped'
