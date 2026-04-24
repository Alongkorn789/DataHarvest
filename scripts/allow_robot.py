import time
import requests
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup

class PoliteCrawler:
    def __init__(self, base_url, user_agent="MyBot/1.0", default_delay=2):
        print("1 init")
        self.base_url = self.normalize_url(base_url)
        self.user_agent = user_agent
        self.default_delay = default_delay
        self.last_request_time = 0
   
        self.rp = RobotFileParser()
        parsed_base = urlparse(self.base_url)
        domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
        self.rp.set_url(f"{domain}/robots.txt")
        
        try:
            self.rp.read()
            print(f"อ่าน robots.txt จาก {domain} สำเร็จ")
        except:
            print("อ่าน robots.txt ไม่ได้ จะใช้ default policy")


    
    def normalize_url(self, url):
        #print("normalize_url")
        parsed = urlparse(url)
        
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".lower().rstrip('/')
        return normalized

    def wait_if_needed(self):
        print("wait_if_needed") 
        delay = self.rp.crawl_delay(self.user_agent)
        if delay is None:
            delay = self.default_delay
        
        elapsed = time.time() - self.last_request_time
        if elapsed < delay:
            sleep_time = delay - elapsed
            print(f"wait_if_needed รอ {sleep_time:.2f} วินาที...")
            time.sleep(sleep_time)

    def can_fetch(self, url):
        print("can_fetch")
        return self.rp.can_fetch(self.user_agent, url)

    def fetch(self, url):
        print("fetch")
        if not self.can_fetch(url):
            print(f"[Blocked by robots.txt]: {url}")
            return None
        
        self.wait_if_needed()
        
        headers = {"User-Agent": self.user_agent}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                print(f"fetch ดึงสำเร็จ: {url}")
                return response.text
            else:
                print(f"Status Code: {response.status_code} สำหรับ {url}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def extract_links(self, html, current_url):
        print("extract_links")
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        
        for a in soup.find_all("a", href=True):
            full_url = urljoin(current_url, a["href"])
            normalized_url = self.normalize_url(full_url)
            
            if urlparse(normalized_url).netloc == urlparse(self.base_url).netloc:
                links.add(normalized_url)
        
        
        #return list(links)
        return sorted(links)

    def crawl(self, start_url, max_pages=5):
        print("2 crawl")
        start_url = self.normalize_url(start_url)
        visited = set()
        to_visit = [start_url]

        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            print("url = to_visit.pop(0)",url)
            
            if url in visited:
                print("url in visited")
                continue
            
            html = self.fetch(url)
            if html is None:
                visited.add(url)
                print("if html is None visited.add(url)",visited) 
                continue
            
            visited.add(url)
            print("visited",visited)
            
            links = self.extract_links(html, url)

            print('links',links)

            """
            for link in links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)
                    print("to_visit.append(link)",to_visit)
            """


            
            for link in links:
                if link in visited:
                    print("already visited เคยเยี่ยมชมแล้ว", link)
                elif link in to_visit:
                    print("already queued เข้าคิวแล้ว", link)
                else:
                    print("new link", link)
                    to_visit.append(link)     



        print(f"\nสรุปผล: Crawl เสร็จสิ้น รวม {len(visited)} URL")

crawler = PoliteCrawler("https://x-raybangkok.com/")
crawler.crawl("http://x-raybangkok.com", max_pages=20)