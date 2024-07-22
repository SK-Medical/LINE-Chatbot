'''
Author: Ayden Lamparski
contact information: ayden@lamparski.com
'''

import json
import requests
import hashlib
import hmac
import base64
from typing import Any, Dict
from assistant import create_run, complete_run, get_thread_messages
from database import get_or_create_thread_id
from utils import log_message
from config import LINE_CONFIG

CHANNEL_SECRET = LINE_CONFIG['channel_secret']
CHANNEL_ACCESS_TOKEN = LINE_CONFIG['access_token']

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for processing incoming LINE messages.

    Args:
        event (Dict[str, Any]): The event data.
        context (Any): The context data.

    Returns:
        Dict[str, Any]: The response dictionary.
    """
    log_message('info', f"Event received: {json.dumps(event, default=str)}")

    headers = event.get('headers', {})
    body = event.get('body', '{}')

    if not verify_signature(headers, body):
        return {
            'statusCode': 403,
            'body': json.dumps('Invalid signature')
        }

    body = json.loads(body)
    events = body.get('events', [])

    for event in events:
        if event['type'] == 'message' and event['message']['type'] == 'text':
            reply_token = event['replyToken']
            line_id = event['source']['userId']
            user_message = event['message']['text']
            log_message('info', f"User message received: {user_message}")
            response_message = handle_user_message(line_id, user_message)
            send_line_reply(reply_token, response_message)

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }

def verify_signature(headers: Dict[str, str], body: str) -> bool:
    """
    Verify the request signature.

    Args:
        headers (Dict[str, str]): The request headers.
        body (str): The request body.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    signature = headers.get('x-line-signature')
    if not signature:
        log_message('error', "Missing signature header")
        return False

    hash = hmac.new(CHANNEL_SECRET.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
    generated_signature = base64.b64encode(hash).decode('utf-8')
    is_valid = hmac.compare_digest(signature, generated_signature)
    if not is_valid:
        log_message('error', "Invalid signature")
    return is_valid

def handle_user_message(line_id: str, user_message: str) -> str:
    """
    Handle the user message and generate a response.

    Args:
        line_id (str): The user's LINE ID.
        user_message (str): The user's message.

    Returns:
        str: The response message.
    """
    try:
        thread_id = get_or_create_thread_id(line_id)
        log_message('info', f"Thread ID: {thread_id}")

        new_message = [{"role": "user", "content": user_message}]
        run = create_run(thread_id, new_message)
        run_status = complete_run(run)
        messages = get_thread_messages(thread_id)
        response_message = ""
        if messages['data']:
            sorted_messages = sorted(messages['data'], key=lambda x: x['created_at'], reverse=True)
            most_recent_message = sorted_messages[0]
            for content_part in most_recent_message["content"]:
                if content_part["type"] == "text":
                    response_message = content_part["text"]["value"]
                    break

        return response_message

    except Exception as e:
        log_message('error', f"Error processing request: {e}")
        return "Sorry, something went wrong."

def send_line_reply(reply_token: str, message: str) -> None:
    """
    Send a reply message back to the user via the LINE API.

    Args:
        reply_token (str): The reply token for the LINE message.
        message (str): The message to send.
    """
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'replyToken': reply_token,
        'messages': [{'type': 'text', 'text': message}]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        log_message('info', f"Reply message sent: {message}")
    else:
        log_message('error', f"Error sending reply: {response.status_code} {response.text}")
