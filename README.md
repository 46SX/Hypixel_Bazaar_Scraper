# Hypixel Bazaar Scraper

A real-time data scraper and logger for the Hypixel Skyblock Bazaar. Fetches live price data from the official Hypixel API and stores it in a local SQLite database for trend analysis.

---
## Features

- Fetches live bazaar data from the Hypixel API every 5 minutes
- Stores historical price data in SQLite
- Push notifications via ntfy
- Tracks all bazaar items automatically
- No API key required — the Bazaar endpoint is public
- 
---

## Data Collected Per Item

| Field | Description |
|---|---|
| `buy_price` | Highest buy order (instant sell price) |
| `sell_price` | Lowest sell offer (instant buy price) |
| `profit_margin` | Difference between buy and sell price |
| `profit_percent` | Profit margin in percent |
| `spread_percent` | Avg buy vs avg sell difference — great for finding flips |
| `average_sell_price` | Weighted average of sell orders |
| `average_buy_price` | Weighted average of buy orders |
| `average_sold_each_day` | Items sold per day (based on weekly moving data) |
| `average_bought_each_day` | Items bought per day (based on weekly moving data) |
| `order_density` | Total market activity (buy + sell orders) |
| `buy_to_sell_ratio` | Demand vs supply ratio |

---

## Getting Started

### Requirements
- Python 3.12
- ntfy server (optional, for notifications)

### 1. Install dependencies
```bash
pip install requests python-dotenv
```

### 2. Create your `.env` file

```
NTFY_URL=http://your-ntfy-server/BazaarTracker
```

Data is saved to `~/data/scraper/bazaar/bazaar.db` automatically.

---
## API

Uses the official Hypixel Public API v2:
```
https://api.hypixel.net/v2/skyblock/bazaar
```
No API key required. Scrapes every 5 minutes to stay well within rate limits.

---

## Project Structure

```
HypixelBazaarChecker/
├── main.py          # Entry point, threading, main loop
├── scraper.py       # Fetches data from Hypixel API
├── utils.py         # Data processing + SQLite logging
├── notis.py         # ntfy push notifications
└── .env             # Not committed — add your own
```

---
## Built With

- Python 3.12
- SQLite3
- ntfy

---
## License

MIT
