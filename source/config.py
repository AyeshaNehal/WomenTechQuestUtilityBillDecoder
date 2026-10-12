import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

MODEL_PROVIDER = os.getenv('MODEL_PROVIDER', 'google')
MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-3.5-flash-lite')
FALLBACK_MODEL = 'gemini-3.1-flash-lite'
API_KEY = os.getenv('API_KEY', '')

EXTRACTION_PROMPT_VERSION = 'v1.0'
DAILY_QUOTA = 500
WARNING_QUOTA = 350
RATE_LIMIT_DELAY = 5.0  # seconds between calls (approx 12 req/min)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
AUDIT_DIR = os.path.join(BASE_DIR, 'audit')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
USAGE_FILE = os.path.join(BASE_DIR, 'usage_report.json')

for d in [CACHE_DIR, AUDIT_DIR, OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)
