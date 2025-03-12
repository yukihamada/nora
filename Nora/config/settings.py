"""
Settings module for Nora.
Defines environment variables and their default values.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Model settings
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Web browsing settings
USE_PUPPETEER = os.getenv("USE_PUPPETEER", "true").lower() == "true"
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"

# GitHub settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")

# AWS settings
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Google Cloud settings
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
GCP_CREDENTIALS_FILE = os.getenv("GCP_CREDENTIALS_FILE", "")

# Stripe settings
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Google AdSense settings
ADSENSE_CLIENT_ID = os.getenv("ADSENSE_CLIENT_ID", "")
ADSENSE_CLIENT_SECRET = os.getenv("ADSENSE_CLIENT_SECRET", "")

# Google Ads settings
GOOGLE_ADS_CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID", "")
GOOGLE_ADS_CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET", "")
GOOGLE_ADS_DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "")
GOOGLE_ADS_REFRESH_TOKEN = os.getenv("GOOGLE_ADS_REFRESH_TOKEN", "")

# Namecheap settings
NAMECHEAP_API_KEY = os.getenv("NAMECHEAP_API_KEY", "")
NAMECHEAP_USERNAME = os.getenv("NAMECHEAP_USERNAME", "")
NAMECHEAP_CLIENT_IP = os.getenv("NAMECHEAP_CLIENT_IP", "")