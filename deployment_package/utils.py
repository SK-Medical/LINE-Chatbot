import requests
import json
import xmlrpc.client
import logging
from typing import Any, Dict, Optional, Tuple
from config import ODOO_CONFIG

def log_message(level: str, message: str) -> None:
    """
    Logs a message at the specified level, sets up logging configuration if not already done.

    Args:
        level (str): The logging level ('debug', 'info', 'warning', 'error', 'critical').
        message (str): The message to log.
    """
    logger = logging.getLogger(__name__)

    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    level = level.lower()
    if level == 'debug':
        logger.debug(message)
    elif level == 'info':
        logger.info(message)
    elif level == 'warning':
        logger.warning(message)
    elif level == 'error':
        logger.error(message)
    elif level == 'critical':
        logger.critical(message)
    else:
        logger.info(message)

def make_request(method: str, url: str, headers: Dict[str, str], data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Makes an HTTP request and returns the JSON response.

    Args:
        method (str): The HTTP method (GET, POST).
        url (str): The URL to send the request to.
        headers (Dict[str, str]): The headers to include in the request.
        data (Optional[Dict[str, Any]]): The data to include in the request.

    Returns:
        Dict[str, Any]: The JSON response.

    Raises:
        Exception: If the request fails.
    """
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=json.dumps(data))
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if response.status_code != 200:
            raise Exception(f"Failed request: {response.text}")

        response_json = response.json()
        if 'error' in response_json:
            raise Exception(f"Error in response: {response_json['error']['message']}")

        return response_json
    except Exception as e:
        raise Exception(f"Request failed: {e}\nURL: {url}\nHeaders: {headers}\nData: {data}")

def connect_and_authenticate() -> Tuple[Optional[xmlrpc.client.ServerProxy], Optional[int], str]:
    """
    Connects to the Odoo server and authenticates the user.

    Returns:
        tuple: A tuple containing the models proxy, user ID, and error message (empty if no error).
    """
    url = ODOO_CONFIG["url"]
    db = ODOO_CONFIG["db"]
    username = ODOO_CONFIG["username"]
    password = ODOO_CONFIG["password"]

    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    try:
        version = common.version()
    except Exception as e:
        return None, None, f"Failed to connect to the Odoo server: {e}"

    uid = common.authenticate(db, username, password, {})
    if not uid:
        return None, None, "Authentication failed"

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    return models, uid, ""
