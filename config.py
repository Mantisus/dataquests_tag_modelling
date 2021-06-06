from pathlib import Path

MONGODB_SETTINGS = {
    'host': '127.0.0.1',
    'port': 27017,
    'db': 'dataquest'
}

CATEGORY_URL = "https://community.dataquest.io/latest.json?ascending=false&no_definitions=true&page={page}"
POSTS_URL = "https://community.dataquest.io/t/{post_id}/posts.json?{posts_ids}&include_suggested=true"

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "no-cache",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Connection": "Keep-Alive"
}

LOGGING_LEVEL = "INFO"
REQUESTS_LIMIT = 3

curent_path = Path(__file__)

LOG_PATH = Path(curent_path.parent, 'data', 'logs')
CACHE_PATH = Path(curent_path.parent, 'data', 'cache')
PICKLES_PATH = Path(curent_path.parent, 'data', 'pickles_path')
