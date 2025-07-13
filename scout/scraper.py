from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, BarColumn, TimeElapsedColumn
from statistics import mean
from bs4 import BeautifulSoup

load_dotenv()

class ConcurrentScraper:
    def __init__(self, urls, max_workers=10):
        self.urls = urls
        self.max_workers = max_workers
        self.results = []
        self.failures = 0
        self.latencies = []
        self.completed = 0

        # ADAPTIVE RATE CONTROL
        self.sleep_time = 0.0   # current delay between tasks
        self.max_latency = 2.0  # latency threshold (seconds)
        self.max_failures = 3   # in last N
        mongo_uri = os.getenv("MONGO_URI")
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client["scout_db"]
        self.collection = self.db["scrape_results"]
        self.adaptive = True

    def fetch(self, url):
        start = time.time()
        try:
            response = requests.get(url, timeout=5)
            latency = time.time() - start
            html_content = response.text

            soup = BeautifulSoup(html_content, "html.parser")
            text_snippet = soup.get_text(separator=' ', strip=True)[:200]

            return (url, response.status_code, latency, html_content, text_snippet)
        except Exception as e:
            latency = time.time() - start
            self.failures += 1
            return (url, None, latency, "", "")


    def build_table(self):
        table = Table(title="Scout Scrapper Live Stats")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Completed", str(self.completed))
        table.add_row("Failures", str(self.failures))
        avg_lat = f"{mean(self.latencies):.2f}s" if self.latencies else "0.00s"
        table.add_row("Avg Latency", avg_lat)
        table.add_row("Workers", str(self.max_workers))
        return table

    def run(self):
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("Scraping...", total=len(self.urls))

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self.fetch, url) for url in self.urls]
                for future in as_completed(futures):
                    url, status, latency, html_content, text_snippet = future.result()
                    self.latencies.append(latency)
                    self.completed += 1
                    self.results.append((url, status, latency))

                    self.collection.insert_one({
                        "url": url,
                        "status": status,
                        "latency": latency,
                        "timestamp": datetime.now(),
                        "html": html_content,
                        "snippet": text_snippet
                    })
                    
                    # ADAPTIVE CONTROL
                    if self.adaptive:
                        avg_lat = mean(self.latencies[-10:]) if len(self.latencies) >= 10 else mean(self.latencies)
                        if avg_lat > self.max_latency or self.failures > self.max_failures:
                            self.sleep_time = min(self.sleep_time + 0.1, 2.0)
                        else:
                            self.sleep_time = max(self.sleep_time - 0.05, 0.0)
                    else:
                        avg_lat = mean(self.latencies[-10:]) if len(self.latencies) >= 10 else mean(self.latencies)

                    if self.sleep_time > 0:
                        time.sleep(self.sleep_time)

                    progress.update(
                        task,
                        advance=1,
                        description=f"Done: {self.completed}, Fail: {self.failures}, Avg Lat: {avg_lat:.2f}s, Sleep: {self.sleep_time:.2f}s"
                    )

        self.show_summary()

    def show_summary(self):
        success_count = sum(1 for _, status, _ in self.results if status == 200)
        avg_latency = mean(self.latencies) if self.latencies else 0
        print(f"\nScraped {len(self.urls)} URLs with {self.max_workers} workers")
        print(f"Success: {success_count}, Failures: {self.failures}")
        print(f"Avg latency: {avg_latency:.2f}s")
