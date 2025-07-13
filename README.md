# 🚀 Scout Scrapper

**Scout Scrapper** is a smart concurrent web scrapper that:

- 🧵 Uses a **multi-threaded architecture** to achieve up to **6x faster scraping** over single-threaded baselines.
- ⚖️ Features **adaptive rate limiting**, automatically slowing down under high latency or error rates to prevent HTTP 429 bans.
- 🗂 Stores **full HTML content** and a short **text snippet** of each page in **MongoDB**, enabling later analysis, indexing, or NLP.
- 📊 Provides a **real-time CLI dashboard** showing completed requests, failures, average latency, and dynamic sleep adjustments.

---

## 📸 Example run

```

Done: 20, Fail: 0, Avg Lat: 2.60s, Sleep: 0.90s ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:09
Scraped 20 URLs with 10 workers
Success: 20, Failures: 0
Avg latency: 2.58s

````

---

## 🚀 Benchmark Results

| Mode              | Total Time | Improvement |
|-------------------|------------|-------------|
| Single-threaded   | 56.46 s    | baseline    |
| Multi-threaded    | 8.94 s     | ~6.3x faster|
| Adaptive Throttle | 11.00 s    | ~5.1x faster|

Benchmarked over 20 real news and media URLs with simulated delays.

---

## 🔍 What does it store?

Each scraped page is saved in MongoDB like:

```json
{
  "url": "https://www.bbc.com",
  "status": 200,
  "latency": 1.74,
  "timestamp": "2025-07-13T19:15:22.234Z",
  "html": "<!doctype html><html>...</html>",
  "snippet": "BBC Homepage World Business Technology ..."
}
````

## 🛠️ Tech Stack

* **Python** with `ThreadPoolExecutor` for concurrency
* **Rich** for live dashboards
* **BeautifulSoup** for text extraction
* **MongoDB** (Atlas or local) for persistence
* **Dotenv** for secure environment configs

---

## 🚀 How to run

### 🔥 Install dependencies

```bash
pip install -r requirements.txt
```

### 📂 Add your `.env`

```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true
```

### 🚀 Run it

```bash
python main.py 10 True
```

* `10` = number of concurrent workers
* `True` = adaptive throttling on

### ⚡ Benchmark modes

```bash
python benchmark.py
```

Runs single-threaded, multi-threaded, and adaptive, printing timing comparisons.
