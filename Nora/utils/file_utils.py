"""
File utilities for Nora.
"""

import os
import shutil
import logging
import tempfile
from typing import List, Optional, BinaryIO, Union, Dict, Any
import json
import yaml

logger = logging.getLogger("nora.file_utils")

def ensure_directory(directory: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory (str): Directory path
        
    Returns:
        bool: True if directory exists or was created, False otherwise
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {str(e)}")
        return False

def list_files(directory: str, pattern: Optional[str] = None) -> List[str]:
    """
    List files in a directory, optionally filtered by pattern.
    
    Args:
        directory (str): Directory path
        pattern (str, optional): Glob pattern to filter files
        
    Returns:
        List[str]: List of file paths
    """
    import glob
    
    if not os.path.exists(directory):
        logger.warning(f"Directory does not exist: {directory}")
        return []
    
    if pattern:
        return glob.glob(os.path.join(directory, pattern))
    else:
        return [os.path.join(directory, f) for f in os.listdir(directory) 
                if os.path.isfile(os.path.join(directory, f))]

def read_file(file_path: str, binary: bool = False) -> Union[str, bytes, None]:
    """
    Read content from a file.
    
    Args:
        file_path (str): Path to the file
        binary (bool): Whether to read in binary mode
        
    Returns:
        Union[str, bytes, None]: File content or None if error
    """
    try:
        mode = 'rb' if binary else 'r'
        with open(file_path, mode) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return None

def write_file(file_path: str, content: Union[str, bytes], binary: bool = False) -> bool:
    """
    Write content to a file.
    
    Args:
        file_path (str): Path to the file
        content (Union[str, bytes]): Content to write
        binary (bool): Whether to write in binary mode
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        mode = 'wb' if binary else 'w'
        with open(file_path, mode) as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing to file {file_path}: {str(e)}")
        return False

def append_file(file_path: str, content: Union[str, bytes], binary: bool = False) -> bool:
    """
    Append content to a file.
    
    Args:
        file_path (str): Path to the file
        content (Union[str, bytes]): Content to append
        binary (bool): Whether to append in binary mode
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        mode = 'ab' if binary else 'a'
        with open(file_path, mode) as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error appending to file {file_path}: {str(e)}")
        return False

def delete_file(file_path: str) -> bool:
    """
    Delete a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
        return False

def copy_file(source: str, destination: str) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        source (str): Source file path
        destination (str): Destination file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        directory = os.path.dirname(destination)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        logger.error(f"Error copying file from {source} to {destination}: {str(e)}")
        return False

def create_temp_file(content: Union[str, bytes] = None, suffix: str = None) -> str:
    """
    Create a temporary file.
    
    Args:
        content (Union[str, bytes], optional): Content to write to the file
        suffix (str, optional): File suffix
        
    Returns:
        str: Path to the temporary file
    """
    try:
        fd, path = tempfile.mkstemp(suffix=suffix)
        
        if content:
            with os.fdopen(fd, 'wb' if isinstance(content, bytes) else 'w') as f:
                f.write(content)
        else:
            os.close(fd)
            
        return path
    except Exception as e:
        logger.error(f"Error creating temporary file: {str(e)}")
        return None

def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load JSON from a file.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        Dict[str, Any]: Parsed JSON data or empty dict if error
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {str(e)}")
        return {}

def save_json_file(file_path: str, data: Dict[str, Any], pretty: bool = True) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        file_path (str): Path to the JSON file
        data (Dict[str, Any]): Data to save
        pretty (bool): Whether to format the JSON with indentation
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(file_path, 'w') as f:
            if pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {str(e)}")
        return False

def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    Load YAML from a file.
    
    Args:
        file_path (str): Path to the YAML file
        
    Returns:
        Dict[str, Any]: Parsed YAML data or empty dict if error
    """
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading YAML from {file_path}: {str(e)}")
        return {}

def save_yaml_file(file_path: str, data: Dict[str, Any]) -> bool:
    """
    Save data to a YAML file.
    
    Args:
        file_path (str): Path to the YAML file
        data (Dict[str, Any]): Data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        return True
    except Exception as e:
        logger.error(f"Error saving YAML to {file_path}: {str(e)}")
        return False