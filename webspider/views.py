from django.shortcuts import render
from django.http import HttpResponse

import threading
from queue import Queue
from .spider import Spider
from .domain import *
from .general import *
import csv

def home(request):
    return render(request, 'index.html')

def find(request):
    url = request.GET['base_url']
    PROJECT_NAME = "myproj"
    HOMEPAGE = url
    DOMAIN_NAME = get_domain_name(HOMEPAGE)
    QUEUE_FILE = PROJECT_NAME + '/queue.txt'
    CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
    ERROR_FILE = PROJECT_NAME + '/errors.csv'
    NUMBER_OF_THREADS = 32
    queue = Queue()
    Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME)


    # Create worker threads (will die when main exits)
    def create_workers():
        for _ in range(NUMBER_OF_THREADS):
            t = threading.Thread(target=work)
            t.daemon = True
            t.start()


    # Do the next job in the queue
    def work():
        while True:
            url = queue.get()
            Spider.crawl_page(threading.current_thread().name, url)
            queue.task_done()


    # Each queued link is a new job
    def create_jobs():
        for link in file_to_set(QUEUE_FILE):
            queue.put(link)
        queue.join()
        crawl()


    # Check if there are items in the queue, if so crawl them
    def crawl():
        queued_links = file_to_set(QUEUE_FILE)
        if len(queued_links) > 0:
            print(str(len(queued_links)) + ' links in the queue')
            create_jobs()


    create_workers()
    crawl()

    urls = []
    status_code = []
    with open(ERROR_FILE, 'r') as csv_file:
        csvreader = csv.reader(csv_file)
        for row in csvreader:
            if(len(row) != 0):
                urls.append(row[0])
                status_code.append(row[1])
    total_urls = file_to_set(CRAWLED_FILE)
    errcount = len(urls)
    urlscount = len(total_urls)
    healthycount = urlscount - errcount
    url_info = list(zip(urls, status_code))
    #print(url_info)
    percentage = int((healthycount / urlscount) * 100)
    return render(request, 'index.html', {'result' : url_info, 'err' : errcount, 'total' : urlscount, 'healthy' : healthycount, 'per' : percentage})
