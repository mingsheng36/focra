import subprocess
from subprocess import PIPE
from django.shortcuts import render
import threading
from django.http import HttpResponse
from scrapy.utils.jsonrpc import jsonrpc_client_call

def index(request):  
#     context_dict = {'boldmessage': "I am bold font from the context"}
    
    return render(request, 'index.html')

def stopCrawl(request):
    if request.method == 'GET':
        #for x in jsonrpc_client_call("http://localhost:6080", 'crawler/spiders', 'list'):
        #    print(x)
        stats = jsonrpc_client_call("http://localhost:6080/stats", 'get_stats')
        for name, value in stats.items():
            print("%-40s %s" % (name, value))
        return HttpResponse("Crawl Stopped")
    return HttpResponse("Failed to stop")

def startCrawl(request):
    if request.method == 'GET':
        threading.Thread(target=crawlSpider).start()
        return HttpResponse("Crawl Started!")
    return HttpResponse("Crawl failed")

def crawlSpider():
    p = subprocess.Popen(["scrapy", "crawl", "focras"], stderr=PIPE)    
    while True:
        o = p.stderr.readline()
        print o
        if o == '' and p.poll() != None: break
    return
    