import requests
import json
from typing import Any, Dict, Optional

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
