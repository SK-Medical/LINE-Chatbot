import boto3
from botocore.exceptions import ClientError
from typing import Dict
from config import AWS_CONFIG, OPENAI_CONFIG, INITIAL_MESSAGE
from assistant import create_thread
from utils import make_request, log_message

dynamodb = boto3.resource('dynamodb', region_name=AWS_CONFIG['region_name'])

def get_or_create_thread_id(line_id: str) -> str:
    """
    Retrieves or creates a thread ID for the given line_id. If the user is new,
    an initial message is sent to start the conversation.

    Args:
        line_id (str): The line ID of the user.

    Returns:
        str: The thread ID associated with the line ID.
    """
    table_name = AWS_CONFIG['table_name']
    table = dynamodb.Table(table_name)

    try:
        response = table.get_item(Key={'line_id': line_id})
        if 'Item' in response:
            return response['Item']['thread_id']
        else:
            thread_id = create_thread()
            send_initial_message(thread_id, INITIAL_MESSAGE)
            table.put_item(Item={'line_id': line_id, 'thread_id': thread_id})
            return thread_id
    except ClientError as e:
        log_message('error', f"Failed to retrieve or create thread ID: {e}")
        raise Exception(f"Failed to retrieve or create thread ID: {e}")

def send_initial_message(thread_id: str, message: str) -> None:
    """
    Sends an initial message to a new thread.

    Args:
        thread_id (str): The thread ID.
        message (str): The initial message to be sent.
    """
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_CONFIG['api_key']}",
        "OpenAI-Beta": "assistants=v2"
    }
    data = {
        "role": "assistant",
        "content": message
    }

    make_request('POST', url, headers, data)

def is_new_user(line_id: str) -> bool:
    """
    Checks if the LINE ID is new.

    Args:
        line_id (str): The LINE ID of the user.

    Returns:
        bool: True if the user is new, False otherwise.
    """
    table_name = AWS_CONFIG['table_name']
    table = dynamodb.Table(table_name)

    try:
        response = table.get_item(Key={'line_id': line_id})
        return 'Item' not in response
    except ClientError as e:
        log_message('error', f"Failed to check if user is new: {e}")
        raise Exception(f"Failed to check if user is new: {e}")
