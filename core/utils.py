"""
Utility functions for SimpleAI framework.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path


logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """
    Configure logging based on LOG_LEVEL environment variable.
    
    Supports: DEBUG, INFO, WARNING, ERROR, CRITICAL
    Default: INFO
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Map string levels to logging constants
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    # Get numeric level, default to INFO if invalid
    numeric_level = level_map.get(log_level, logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set SimpleAI loggers to the same level
    for logger_name in ['simpleai.config', 'simpleai.agent', 'simpleai.collaborate', 'simpleai.utils']:
        logging.getLogger(logger_name).setLevel(numeric_level)
    
    logger.debug(f"Logging configured to level: {log_level}")


# Configure logging when the module is imported
configure_logging()


def load_env_file(env_file: str = ".env") -> None:
    """
    Load environment variables from a .env file.
    Searches in script directory, parent directory, and grandparent directory.

    Args:
        env_file: Path to the environment file
    """
    import inspect

    if os.path.isabs(env_file):
        # Absolute path provided
        search_paths = [Path(env_file)]
    else:
        # Relative path - search up the directory tree
        caller_frame = inspect.stack()[1]
        caller_dir = Path(caller_frame.filename).parent

        search_paths = [
            caller_dir / env_file,  # Same directory as script
            caller_dir.parent / env_file,  # Parent directory (project root)
            caller_dir.parent.parent / env_file  # Grandparent directory
        ]

    for env_path in search_paths:
        if env_path.exists():
            logger.debug(f"Found environment file at: {env_path.absolute()}")
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip('\r\n\t\0 ')  # Also strip null characters
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().replace('\0', '')  # Remove null chars
                        value = value.strip().strip('"').strip("'").replace('\0', '')  # Remove null chars
                        if key and value:  # Only set if both are non-empty
                            os.environ[key] = value
            logger.debug(f"Loaded environment variables from {env_path}")
            return

    # Not found in any location
    searched = [str(p.absolute()) for p in search_paths]
    logger.warning(f"Environment file {env_file} not found. Searched: {searched}")


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    Rough approximation: 1 token ≈ 4 characters
    
    Args:
        text: The text to estimate tokens for
        
    Returns:
        Estimated token count
    """
    return len(text) // 4


def format_tool_schema(func_name: str, description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a tool schema for API calls.
    
    Args:
        func_name: Function name
        description: Function description
        parameters: Parameter schema
        
    Returns:
        Formatted tool schema
    """
    return {
        "type": "function",
        "function": {
            "name": func_name,
            "description": description,
            "parameters": parameters
        }
    }


def extract_json_from_string(text: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """
    Extract JSON from a string that might contain other text.
    
    Args:
        text: String potentially containing JSON
        
    Returns:
        Extracted JSON as dict/list or None
    """
    if not text or not text.strip():
        return None
        
    # Try to find JSON-like content (array or object)
    array_start = text.find('[')
    object_start = text.find('{')
    
    # Determine which comes first
    if array_start == -1 and object_start == -1:
        return None
    
    if array_start != -1 and (object_start == -1 or array_start < object_start):
        # Extract array
        start_idx = array_start
        start_char = '['
        end_char = ']'
    else:
        # Extract object
        start_idx = object_start
        start_char = '{'
        end_char = '}'
    
    # Find matching closing bracket/brace
    count = 0
    end_idx = start_idx
    
    for i in range(start_idx, len(text)):
        if text[i] == start_char:
            count += 1
        elif text[i] == end_char:
            count -= 1
            if count == 0:
                end_idx = i
                break
    
    if count != 0:
        return None
        
    try:
        json_str = text[start_idx:end_idx + 1]
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Try to fix common JSON issues like unescaped control characters
        try:
            fixed_json = _fix_json_control_chars(json_str)
            return json.loads(fixed_json)
        except json.JSONDecodeError:
            return None


def _fix_json_control_chars(json_str: str) -> str:
    """Fix JSON strings with unescaped control characters."""
    import re
    
    # Pattern to find string values (between quotes, handling escaped quotes)
    string_pattern = r'"([^"\\]*(\\.[^"\\]*)*)"'
    
    def fix_string_content(match):
        content = match.group(1)
        # Fix control characters within the string content
        fixed_content = (content
                        .replace('\n', '\\n')
                        .replace('\r', '\\r') 
                        .replace('\t', '\\t')
                        .replace('\b', '\\b')
                        .replace('\f', '\\f'))
        return f'"{fixed_content}"'
    
    # Apply the fix to all string values
    fixed_json = re.sub(string_pattern, fix_string_content, json_str)
    return fixed_json


def sanitize_message_content(content: Union[str, List, Dict, None]) -> str:
    """
    Sanitize message content to ensure it's a valid string.
    
    Args:
        content: Content to sanitize
        
    Returns:
        Sanitized string content
    """
    if content is None:
        return ""
    elif isinstance(content, str):
        return content
    elif isinstance(content, (list, dict)):
        return json.dumps(content, ensure_ascii=False)
    else:
        return str(content)


def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries, with override taking precedence.
    
    Args:
        base: Base dictionary
        override: Override dictionary
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if value is not None:  # Only override if value is not None
            result[key] = value
    return result