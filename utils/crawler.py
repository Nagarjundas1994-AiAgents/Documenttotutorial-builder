import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urljoin, urlparse
import asyncio

class Crawler:
    def __init__(self, base_url, max_depth=2):
        self.base_url = base_url
        self.base_netloc = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.visited_urls = set()
        self.text_converter = html2text.HTML2Text()
        self.text_converter.ignore_links = True
        self.text_converter.ignore_images = True

    async def crawl(self):
        queue = [(self.base_url, 0)]
        self.visited_urls.add(self.base_url)
        
        all_pages_content = []

        while queue:
            current_url, depth = queue.pop(0)
            
            if depth > self.max_depth:
                continue

            print(f"Crawling [Depth {depth}]: {current_url}")
            
            try:
                response = await asyncio.to_thread(requests.get, current_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'lxml')
                
                # Extract clean text
                text_content = self.text_converter.handle(soup.prettify())
                if text_content and len(text_content.split()) > 50: # Basic filter for meaningful content
                    all_pages_content.append({"url": current_url, "content": text_content})
                    yield {"type": "page_crawled", "url": current_url, "content_length": len(text_content)}

                # Find and queue new links
                if depth < self.max_depth:
                    for a_tag in soup.find_all('a', href=True):
                        link = a_tag['href']
                        full_url = urljoin(self.base_url, link)
                        parsed_url = urlparse(full_url)
                        
                        # Normalize URL
                        normalized_url = parsed_url._replace(fragment="", query="").geturl()

                        if (parsed_url.netloc == self.base_netloc and 
                            normalized_url not in self.visited_urls and
                            not normalized_url.endswith(('.pdf', '.zip', '.jpg', '.png'))):
                            
                            self.visited_urls.add(normalized_url)
                            queue.append((normalized_url, depth + 1))
                            yield {"type": "url_found", "url": normalized_url}

            except requests.RequestException as e:
                print(f"Error crawling {current_url}: {e}")
                yield {"type": "error", "url": current_url, "message": str(e)}
        
        yield {"type": "crawl_complete", "total_pages": len(all_pages_content), "content": all_pages_content}