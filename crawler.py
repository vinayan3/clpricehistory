from BeautifulSoup import BeautifulSoup
import urllib2, random, re, sqlite3, logging
import urlparse
import time
import list_parser
import traceback
import sys

LOG_LEVEL  = logging.INFO
 
class WebCrawler:
    def __init__(self, logging_level=LOG_LEVEL):
        logging.basicConfig(level=logging_level)

        self.urlList = []
        self.urlSet = set()
  
    def _pop_from_list(self):
        if len(self.urlList) > 0:
            poppedUrl = self.urlList.pop()
            
            logging.debug("Next URL: %s", poppedUrl)

            return poppedUrl
        else:
            return None
 
    def _push_to_list(self, url):
        if not url in self.urlSet:
            logging.debug("URL to insert: %s" % url)
            self.urlList.append(url)
            self.urlSet.add(url)
 
    def crawl(self, url, urlPattern):
        work_url = url
        logging.info("Work URL: %s" % work_url)

        while not (work_url is None):
            try:
                page = urllib2.urlopen(work_url)
                        
                soup = BeautifulSoup(page)

                for i in list_parser.parse(soup):
                    i.save()
                
            except Exception as e:
                logging.debug("Failed to parse, attempting to get next URL from DB")

                traceback.print_exception(*sys.exc_info())
                
                work_url = self._pop_from_list()
                logging.info("Error in parsing skipping to url %s", work_url)

                continue

            for link in soup('a'):
                logging.debug("Processing link object: %s" % link)

                for (k,v) in link.attrs:
                    urlCheck = urlparse.urljoin(work_url, v)
                    if k == 'href' and urlPattern.match(urlCheck):
                        self._push_to_list(urlCheck)

            logging.debug("Finished adding URLs")
            logging.debug("Getting a new URL for processing from DB")
            work_url = self._pop_from_list()
            logging.info("Found URL: %s" % work_url)
            time.sleep(10)
 
 
if __name__ == '__main__':
    wc = WebCrawler()
    #crawl the furniture page
    #http://[Some Sub Craigslist].craigslist.org/[optional Some Sub Region]/[a page]
    #urlPattern = re.compile("(http://sfbay\.craigslist\.org/(\w+/)?fu[ado]/.+|index100\.html)")
    #wc.crawl('http://sfbay.craigslist.org/fua/', urlPattern)

    urlPattern = re.compile("(http://sfbay\.craigslist\.org/fua/index\d+\.html)")
    wc.crawl('http://sfbay.craigslist.org/fua/', urlPattern)

    
