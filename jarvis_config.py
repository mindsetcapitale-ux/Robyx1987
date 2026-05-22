# jarvis_config.py

# ==============================
# JARVIS GENERAL CONFIG
# ==============================

APP_NAME = "Jarvis Crypto AI"
VERSION = "1.0.0"

# ==============================
# TELEGRAM
# ==============================

TELEGRAM_ENABLED = True

# Il token e chat id restano dentro telegram_alerts.py per ora.
# Dopo li spostiamo qui o in .env.

# ==============================
# SCAN SETTINGS
# ==============================

FAST_INTERVAL_SECONDS = 1800
SIGNAL_INTERVAL_SECONDS = 3600
DIGEST_INTERVAL_SECONDS = 21600
HEALTH_INTERVAL_SECONDS = 10800

# ==============================
# SIGNAL SETTINGS
# ==============================

MIN_AI_SCORE = 75
MIN_STRONG_SCORE = 85

COOLDOWN_HOURS = 6

# ==============================
# MARKET PHASE SETTINGS
# ==============================

BLOCK_BEARISH_LOW_SCORE = True
MIN_SCORE_BEARISH = 90
MIN_SCORE_SIDEWAYS = 82
MIN_SCORE_NEUTRAL = 78
MIN_SCORE_BULLISH = 75

# ==============================
# RISK SETTINGS
# ==============================

ACCOUNT_SIZE_USD = 1000
MAX_RISK_PER_TRADE_PERCENT = 2
MAX_POSITION_SIZE_PERCENT = 10

# ==============================
# GEM DETECTOR SETTINGS
# ==============================

SEARCH_KEYWORDS = [
    "ai",
    "meme",
    "base",
    "sol",
    "eth",
    "pepe",
    "doge",
]

MIN_LIQUIDITY_USD = 20000
MIN_VOLUME_24H = 15000
MAX_PRICE_CHANGE_24H = 35
MIN_PRICE_CHANGE_24H = -15
MAX_FDV = 50000000

# ==============================
# FILES
# ==============================

SIGNAL_HISTORY_FILE = "jarvis_signal_history.json"
TRADE_JOURNAL_FILE = "trade_journal.json"
MARKET_MEMORY_FILE = "market_memory.json"
COOLDOWN_FILE = "signal_cooldown.json"
LOG_FILE = "jarvis_events_log.json"
CACHE_FILE = "jarvis_api_cache.json"