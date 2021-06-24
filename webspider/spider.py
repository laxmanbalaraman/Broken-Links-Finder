from urllib.request import urlopen, Request
from .link_finder import LinkFinder
from .domain import *
from .general import *
import csv

# this class extracts links for each url
class Spider:

    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    error_file = ''
    queue = set()
    crawled = set()

    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        Spider.error_file = Spider.project_name + '/errors.csv'
        self.boot()
        self.crawl_page('First spider', Spider.base_url)

    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        # check if page is not already visited
        if page_url not in Spider.crawled:
            print(thread_name + ' now crawling ' + page_url)
            print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(page_url))
            Spider.queue.remove(page_url)
            Spider.crawled.add(page_url)
            Spider.update_files()

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            # request for connection
            req = Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
            # open the url contents
            response = urlopen(req)
            if 'text/html' in response.getheader('Content-Type'):
                # read the page contents, return in bytes
                html_bytes = response.read()
                # convert to normal (english) language
                html_string = html_bytes.decode("utf-8")
            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string)
        # check for abnormal links (The main part of the project)
        except Exception as e:
            e = str(e)
            e = e[11:14]
            page_info = []
            page_info.append(page_url)
            page_info.append(e)
            #append_to_file(Spider.error_file, page_url);
            with open(Spider.error_file, 'a+') as csv_file:
                csvwriter = csv.writer(csv_file)
                csvwriter.writerow(page_info)
            return set()
        return finder.page_links()

    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            # check if url is alredy visited if yes, ignore
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            # ignore third party link
            if Spider.domain_name != get_domain_name(url):
                continue
            Spider.queue.add(url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)
