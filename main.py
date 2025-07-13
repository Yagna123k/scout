from scout.scraper import ConcurrentScraper

if __name__ == "__main__":
    import sys

    urls = [
        "https://www.nytimes.com",
        "https://www.bbc.com",
        "https://edition.cnn.com",
        "https://www.theverge.com",
        "https://techcrunch.com",
        "https://arstechnica.com",
        "https://www.cnbc.com",
        "https://www.wired.com",
        "https://www.reuters.com",
        "https://www.nationalgeographic.com"
    ] * 3

    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    adaptive = sys.argv[2].lower() == "true" if len(sys.argv) > 2 else True

    scraper = ConcurrentScraper(urls, max_workers=workers)
    scraper.adaptive = adaptive
    scraper.run()