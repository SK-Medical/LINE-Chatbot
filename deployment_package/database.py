import boto3
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any
from config import AWS_CONFIG
from assistant import create_thread

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name=AWS_CONFIG['region_name'])

def get_or_create_thread_id(line_id: str) -> str:
    """
    Retrieves or creates a thread ID for the given line_id.

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
            table.put_item(Item={'line_id': line_id, 'thread_id': thread_id})
            return thread_id
    except ClientError as e:
        raise Exception(f"Failed to retrieve or create thread ID: {e}")
