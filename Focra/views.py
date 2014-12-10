import subprocess
from subprocess import PIPE
from django.shortcuts import render
#import threading
from django.http import HttpResponse
from scrapy.utils.jsonrpc import jsonrpc_client_call
import re
from models import User

runningCrawlers = {}

####
# welcome page and sign up page
#### 
def index(request):
    # DEVELOPMENT PURPOSE
#     request.session['username'] = 'jayden'
#     return home(request)

    #  FOR PRODUCTION USE
    if request.method == 'GET':      
        return render(request, 'index.html')   
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        request.session['username'] = username
        newUser = User(username=username, password=password).save()
        print newUser
        return home(request)
    else: 
        return render(request, 'index.html')

####
# display home page to authenticated clients
####   
def home(request):
    auth = request.session.get('username');
    if auth:
        print 'authenticated'
        return render(request, 'home.html', {'username': auth})
    else:
        print 'not auth'
        return render(request, 'index.html')

####
# To stop the specific crawler
#### 
def startCrawl(request):
             
    if request.method == 'GET':
        client = request.session.get('username')
        if client:
            scrapyProcess = subprocess.Popen(["scrapy", "crawl", "focras"], stderr=PIPE)    
            while True:
                scrapyOutput = scrapyProcess.stderr.readline()
                scrapyWebAddr = re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[0-9]{1,5}', scrapyOutput)
                if scrapyWebAddr:
                    print scrapyWebAddr
                    
                    #global runningCrawlers
                    #runningCrawlers['username'] = 
                    break;
            print scrapyOutput
#             if o == '' and p.poll() != None: break
        return HttpResponse("Crawl Started!")
#         threading.Thread(target=crawlSpider).start()
       
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



    