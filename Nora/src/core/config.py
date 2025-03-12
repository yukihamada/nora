"""
Configuration module for Nora agent.
Handles loading and managing configuration settings.
"""

import os
import json
import logging
from dotenv import load_dotenv

logger = logging.getLogger("nora.config")

def load_config():
    """
    Load configuration from environment variables and config files.
    
    Returns:
        dict: Configuration dictionary
    """
    # Load environment variables from .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                           "config", ".env")
    load_dotenv(env_path)
    
    # Default configuration
    config = {
        "model": {
            "provider": os.getenv("MODEL_PROVIDER", "openai"),
            "name": os.getenv("MODEL_NAME", "gpt-4"),
            "api_key": os.getenv("OPENAI_API_KEY", ""),
        },
        "web_browsing": {
            "use_puppeteer": os.getenv("USE_PUPPETEER", "true").lower() == "true",
            "headless": os.getenv("BROWSER_HEADLESS", "true").lower() == "true",
        },
        "github": {
            "token": os.getenv("GITHUB_TOKEN", ""),
            "username": os.getenv("GITHUB_USERNAME", ""),
        },
        "cloud": {
            "aws": {
                "access_key": os.getenv("AWS_ACCESS_KEY_ID", ""),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
                "region": os.getenv("AWS_REGION", "us-east-1"),
            },
            "gcp": {
                "project_id": os.getenv("GCP_PROJECT_ID", ""),
                "credentials_file": os.getenv("GCP_CREDENTIALS_FILE", ""),
            },
        },
        "monetization": {
            "stripe": {
                "api_key": os.getenv("STRIPE_API_KEY", ""),
                "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET", ""),
            },
            "adsense": {
                "client_id": os.getenv("ADSENSE_CLIENT_ID", ""),
                "client_secret": os.getenv("ADSENSE_CLIENT_SECRET", ""),
            },
        },
        "ads": {
            "google_ads": {
                "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID", ""),
                "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET", ""),
                "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
                "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN", ""),
            },
        },
        "domains": {
            "namecheap": {
                "api_key": os.getenv("NAMECHEAP_API_KEY", ""),
                "username": os.getenv("NAMECHEAP_USERNAME", ""),
                "client_ip": os.getenv("NAMECHEAP_CLIENT_IP", ""),
            },
        },
    }
    
    # Try to load secrets from JSON file if it exists
    secrets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                               "config", "secrets.json")
    
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
                
            # Merge secrets with config
            _deep_merge(config, secrets)
            logger.info("Loaded configuration from secrets.json")
        except Exception as e:
            logger.error(f"Error loading secrets.json: {str(e)}")
    
    # Validate critical configuration
    _validate_config(config)
    
    return config

def _deep_merge(dict1, dict2):
    """
    Deep merge two dictionaries.
    
    Args:
        dict1 (dict): First dictionary (will be modified)
        dict2 (dict): Second dictionary (values will override dict1)
    """
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            _deep_merge(dict1[key], value)
        else:
            dict1[key] = value

def _validate_config(config):
    """
    Validate critical configuration settings.
    
    Args:
        config (dict): Configuration dictionary
    """
    # Check for critical API keys
    if not config["model"]["api_key"]:
        logger.warning("No model API key provided. Some functionality may be limited.")
    
    # Log configuration status
    logger.info(f"Using model provider: {config['model']['provider']}, model: {config['model']['name']}")
    
    # Check GitHub configuration
    if not config["github"]["token"]:
        logger.warning("No GitHub token provided. GitHub operations will be unavailable.")
    
    # Check cloud configuration
    if not config["cloud"]["aws"]["access_key"] or not config["cloud"]["aws"]["secret_key"]:
        logger.warning("AWS credentials not configured. AWS operations will be unavailable.")
    
    if not config["cloud"]["gcp"]["project_id"] or not config["cloud"]["gcp"]["credentials_file"]:
        logger.warning("GCP credentials not configured. GCP operations will be unavailable.")