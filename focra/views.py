import subprocess, re
from subprocess import PIPE
from django.shortcuts import render, redirect
from django.http import HttpResponse
from scrapy.utils.jsonrpc import jsonrpc_client_call
from models import Crawler

'''
welcome page and sign up page
''' 
def index(request):
    '''
    Development purpose, login as jayden
    '''
    username = 'jayden'
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
Monitor page for crawlers to show stats
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
            request.session['crawlerTemplate']= crawler.crawlerTemplate
            return render(request, 'monitor.html', {'username': username, 'crawlers': crawlers, 'crawler': crawler})
    
'''
To create crawler page
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
            print request.POST['crawlerTemplate']
            crawlerTemplate = request.POST['crawlerTemplate']      
            try:
                crawlerAddr = "127.0.0.1:6080"
                #crawlerAddr = runCrawler(seeds);
                Crawler(crawlerName=crawlerName, 
                        crawlerSeeds=seeds, 
                        crawlerAddr=crawlerAddr, 
                        crawlerStatus='running', 
                        crawlerOwner=username, 
                        crawlerTemplate=crawlerTemplate).save()            
            except Exception, err:
                print err
            request.session['crawlers'] = crawlers + [crawlerName]
            return redirect('/' + username + '/' + crawlerName)
        
    return redirect('/')
 
'''
To update current crawler in session
'''
def updateCrawler(request):
    return

'''
To delete current crawler in session
'''
def deleteCrawler(request):
    if request.method == 'POST':  
        try:
            crawlerName = request.session.get('crawlerName')
            Crawler.objects(crawlerName=crawlerName).delete()
            crawlers = request.session.get('crawlers')
            crawlers.remove(crawlerName)
            request.session['crawlers'] = crawlers
            return HttpResponse(crawlerName + " has been deleted.")
        except Exception, err:
            print err
    return

'''
To handle start crawler requests
'''
def startCrawl(request):  
    if request.method == 'POST':  
        crawlerName = request.session.get('crawlerName')
        crawlerSeeds = request.session.get('crawlerSeeds')
        crawlerTemplate = request.session.get('crawlerTemplate')
        try:
            #crawlerAddr = "127.0.0.1:6080"
            crawlerAddr = runCrawler(crawlerSeeds, crawlerTemplate)
            Crawler.objects(crawlerName=crawlerName).update_one(set__crawlerStatus='running', set__crawlerAddr=crawlerAddr)
            request.session['crawlerAddr'] = crawlerAddr
        except Exception, err:
            print err
        return HttpResponse(crawlerName + ' is running')
    else:
        return HttpResponse("Crawl failed")
        
    return redirect('/')
    
'''
To handle stop crawler requests
'''      
def stopCrawl(request):
    if request.method == 'POST':
        print request.session.get('crawlerAddr')
        crawlerName = request.session.get('crawlerName')
        stopCrawler(request.session.get('crawlerAddr'))
        try:
            Crawler.objects(crawlerName=crawlerName).update_one(set__crawlerStatus='stopped', set__crawlerAddr='')
        except Exception, err:
            print err
        return HttpResponse(crawlerName + ' has been stopped')
    else:
        return HttpResponse("Stop failed")
    return redirect('/')

'''
starting the crawler through cmdline in local machine
needs to be changed to start through http call for scalability
'''  
def runCrawler(seeds, template):
    print template + " - printed on run crawler"
    commands = ["scrapy", "crawl", "focras", "-a", "seeds=" + ''.join(seeds), "-a", "template=" + template]
    crawlerProcess = subprocess.Popen(commands, stderr=PIPE)    
    while True:
        crawlerAddr = re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[0-9]{1,5}', crawlerProcess.stderr.readline())
        if crawlerAddr:
            print crawlerAddr
            break;
    return ''.join(crawlerAddr)

'''
stopping crawler through jsonrpc
'''  
def stopCrawler(addr):
    try: 
        jsonrpc_client_call("http://" + addr + "/crawler/engine", 'close_spider', 'focras')
    except:
        print 'Expected err - ' 

'''
fetch seed url page
'''
# def fetch(request):
#     if request.method == 'GET':
#         print "hi"
#         commands = ["scrapy", "fetch", "http://google.com.sg"]
#         r = ''
#         process = subprocess.Popen(commands, stdout=PIPE)    
#         while True:
#             res = process.stdout.readline()
#             r += res
#             if res == '' and process.poll() != None:
#                 break
#         return render(request, 'overview.html', {'page':r})

# def fetch(request):
#     print 'hi' 
#     #[os.path.join(BASE_DIR, "scripts")]
#     try:  
#         p = subprocess.Popen(["python", os.path.dirname(os.path.dirname(__file__)) +'/scripts/test.py'], stdout=PIPE)  
#         while True:
#             res = p.stdout.readline()
#             if res == '' and p.poll() != None:
#                 break
#             print res
#         return HttpResponse("done")
#     except Exception, err:
#         print err
#     #return render(request, 'overview.html', {'page':(driver.page_source).encode('utf-8')})
    
