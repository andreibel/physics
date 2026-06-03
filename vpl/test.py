import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict

class PlantArticleSearchEngine:
    def __init__(self):
        """Initialize engine for specific academic plant articles"""
        self.pages = []
        self.index = []
        self.word_map = defaultdict(list)
        self.stop_words = {'a', 'an', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'it', 'that', 'which', 'from', 'as', 'by', 'this', 'were', 'was'}

    def fetch_specific_urls(self, urls):
        """Fetch and scrape content from specific academic links"""
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()

                    title = soup.title.string if soup.title else url
                    content = soup.get_text(separator=' ')

                    self.pages.append({
                        'title': title.strip(),
                        'url': url,
                        'content': content
                    })
                    print(f"Successfully fetched: {title.strip()[:50]}...")
                else:
                    print(f"Could not fetch {url} - Status: {response.status_code}")
            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")

    def build_index(self):
        """Build index with required 'term' and 'DocIDs' fields"""
        temp_index = defaultdict(set)
        for i, page in enumerate(self.pages):
            # Tokenize and clean text
            words = re.findall(r'\b[a-z]{3,}\b', page['content'].lower())
            for word in words:
                if word not in self.stop_words:
                    # DocIDs stores the numbered index of the article or its URL
                    temp_index[word].add(page['url'])

        self.index = [{'term': k, 'DocIDs': list(v)} for k, v in temp_index.items()]
        self.word_map = {item['term']: item['DocIDs'] for item in self.index}
        print(f"\nIndex built with {len(self.index)} terms from {len(self.pages)} articles.")

    def search_rag(self, query):
        """Task 4: RAG Implementation"""
        query_words = [w.lower() for w in re.findall(r'\w+', query) if w.lower() not in self.stop_words]
        results_map = defaultdict(int)

        for word in query_words:
            if word in self.word_map:
                for doc_url in self.word_map[word]:
                    results_map[doc_url] += 1

        sorted_docs = sorted(results_map.items(), key=lambda x: x[1], reverse=True)

        print(f"\n--- RAG Results for Query: '{query}' ---\n")
        for url, score in sorted_docs[:3]:
            page = next(p for p in self.pages if p['url'] == url)
            # Simple context extraction
            snippet = page['content'][:300].replace('\n', ' ').strip() + "..."
            print(f"ARTICLE: {page['title']}\nURL: {url}\nRELEVANCE SCORE: {score}\nSNIPPET: {snippet}\n")
            print("-" * 50)

# List of provided URLs
urls = [
    "https://www.cabidigitallibrary.org/doi/full/10.5555/20103087599",
    "https://www.sciencedirect.com/science/article/pii/S0926669019309033",
    "https://www.sciencedirect.com/science/article/pii/S0926669024012925",
    "https://journals.ashs.org/view/journals/hortsci/60/2/article-p208.xml",
    "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0273367"
]

# Execution
engine = PlantArticleSearchEngine()
engine.fetch_specific_urls(urls)
engine.build_index()
# Search for one of the key terms like 'Essential oils' or 'Rosemary'
engine.search_rag("essential oils rosemary drought stress")