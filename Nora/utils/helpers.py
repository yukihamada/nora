"""
Helper utilities for Nora.
"""

import os
import json
import uuid
import logging
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("nora.helpers")

def generate_unique_id() -> str:
    """
    Generate a unique ID for tasks or operations.
    
    Returns:
        str: Unique ID
    """
    return str(uuid.uuid4())

def get_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        str: Current timestamp
    """
    return datetime.now().isoformat()

def hash_content(content: str) -> str:
    """
    Generate a hash for content.
    
    Args:
        content (str): Content to hash
        
    Returns:
        str: SHA-256 hash of the content
    """
    return hashlib.sha256(content.encode()).hexdigest()

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for file systems.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        name = name[:255 - len(ext) - 1]
        filename = name + ext
    
    return filename

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries recursively.
    
    Args:
        dict1 (Dict[str, Any]): First dictionary
        dict2 (Dict[str, Any]): Second dictionary
        
    Returns:
        Dict[str, Any]: Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load JSON from a file.
    
    Args:
        file_path (str): Path to JSON file
        
    Returns:
        Dict[str, Any]: Loaded JSON data
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {str(e)}")
        return {}

def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data (Dict[str, Any]): Data to save
        file_path (str): Path to save JSON file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {str(e)}")
        return False

def chunk_text(text: str, chunk_size: int = 4000) -> List[str]:
    """
    Split text into chunks of specified size.
    
    Args:
        text (str): Text to split
        chunk_size (int): Maximum chunk size
        
    Returns:
        List[str]: List of text chunks
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to a human-readable string.
    
    Args:
        seconds (float): Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"