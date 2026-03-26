import os
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

# 🔥 Coinglass API
BASE_URL = "https://open-api-v4.coinglass.com"
API_KEY = os.getenv("COINGLASS_API_KEY")
