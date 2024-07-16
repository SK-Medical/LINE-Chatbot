import json
import logging
import os
import requests
import hashlib
import hmac
import base64
from assistant import create_run, complete_run, get_thread_messages
from database import get_or_create_thread_id

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Load environment variables
CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

def lambda_handler(event, context):
    logger.info(f"Event received: {json.dumps(event, default=str)}")

    headers = event.get('headers', {})
    body = event.get('body', '{}')

    # Verify the request
    if not verify_signature(headers, body):
        logger.error("Invalid signature")
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

            # Handle the message and generate a response
            response_message = handle_user_message(line_id, user_message)

            # Send the response back to the user
            send_line_reply(reply_token, response_message)

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }

def verify_signature(headers, body):
    signature = headers.get('x-line-signature')
    if not signature:
        logger.error("Missing signature header")
        return False
    if not CHANNEL_SECRET:
        logger.error("Missing LINE channel secret in environment variables")
        return False

    hash = hmac.new(CHANNEL_SECRET.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
    generated_signature = base64.b64encode(hash).decode('utf-8')
    return hmac.compare_digest(signature, generated_signature)

def handle_user_message(line_id, user_message):
    try:
        # Get or create a thread ID for the given line_id
        thread_id = get_or_create_thread_id(line_id)
        logger.info(f"Thread ID: {thread_id}")

        # Create a run with the user message
        additional_messages = [{"role": "user", "content": user_message}]
        run = create_run(thread_id, additional_messages)

        # Complete the run and get the final status
        run_status = complete_run(run)

        # Get the latest messages from the thread
        messages = get_thread_messages(thread_id)
        if messages['data']:
            # Log only the content of the message received
            for message in messages['data']:
                for content_part in message["content"]:
                    if content_part["type"] == "text":
                        logger.info(f"Message received: {content_part['text']['value']}")

        # Extract the most recent response message
        response_message = ""
        if messages['data']:
            # Sort messages by creation time in descending order to get the most recent message first
            sorted_messages = sorted(messages['data'], key=lambda x: x['created_at'], reverse=True)
            most_recent_message = sorted_messages[0]
            for content_part in most_recent_message["content"]:
                if content_part["type"] == "text":
                    response_message = content_part["text"]["value"]
                    break

        return response_message

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return "Sorry, something went wrong."

def send_line_reply(reply_token, message):
    if not CHANNEL_ACCESS_TOKEN:
        logger.error("Missing LINE access token in environment variables")
        return

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
        logger.info(f"Reply message sent: {message}")
    else:
        logger.error(f"Error sending reply: {response.status_code} {response.text}")
