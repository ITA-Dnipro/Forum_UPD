# News  Microservice

## Overview
This microservice scrapes the latest business news from [epravda.com.ua](https://epravda.com.ua/news) and filters relevant articles before storing them in a MongoDB database and caching them in Redis.

---

## Features
- **Asynchronous scraping** using `aiohttp` and `BeautifulSoup`
- **Periodic tasks** using `Celery`, `Celerybeat` and `Redis`
- **News filtering** based on keyword matching
- **Redis caching** for faster retrieval
- **Dockerization**

---

## API Endpoints
| Method | Endpoint              | Description                      |
|--------|-----------------------|----------------------------------|
| GET    | `/api/news`               | Fetch latest news from MongoDB   |
| POST   | `/api/scrape`             | Trigger news scraping manually   |
| GET    | `/api/news/{news_id}`     | Retrieve a specific news article |
| GET    | `/api/news/recent`        | Retrieve news from cache         |
| DELETE | `/api/news/{news_id}`     | Delete specific news             |


## Technologies
- Python 3.10
- FastAPI
- MongoDB
- Redis
- Celery
- Docker & Docker Compose

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.10
- MongoDB
- Docker

### Setup
1. Install all dependencies:
```sh
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
APP_PORT=backend_port (e.g. `8000`, `8001`)
REDIS_URL=redis_url (e.g. `redis://redis_cache:6379/0`)
MONGO_URL=db_url (e.g. `mongodb://mongodb:27017`)
MONGO_DB_NAME=db_name (e.g. `news`)
MAX_POOL_SIZE=max_pool_size (e.g. `100`)
```

3. Build and run containers:
```sh
docker-compose up --build
```