import json
import time
from typing import Any, Dict, List, Optional
from utils import make_request, log_message
from config import OPENAI_CONFIG
from odoo import get_tool_output

def create_thread() -> str:
    """
    Creates a new thread and returns the thread ID.

    Returns:
        str: The ID of the created thread.
    """
    url = "https://api.openai.com/v1/threads"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_CONFIG['api_key']}",
        "OpenAI-Beta": "assistants=v2"
    }
    data = {
        "messages": [{
            "role": "user",
            "content": "you are a helpful assistant"
        }]
    }
    response = make_request('POST', url, headers, data)
    return response["id"]

def create_run(thread_id: str, additional_messages: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Creates a run within a given thread with optional additional messages.

    Args:
        thread_id (str): The ID of the thread.
        additional_messages (Optional[List[Dict[str, Any]]]): Additional messages to include in the run.

    Returns:
        Dict[str, Any]: The created run.
    """
    assistant_id = OPENAI_CONFIG["assistant_id"]
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_CONFIG['api_key']}",
        "OpenAI-Beta": "assistants=v2"
    }

    data = {
        "assistant_id": assistant_id
    }

    if additional_messages:
        data["additional_messages"] = additional_messages

    try:
        result = make_request('POST', url, headers, data)
        log_message('info', f"Run started: {result}")
        return result
    except Exception as e:
        error_message = str(e)
        log_message("error", f"Error when making run: {error_message}")
        if "already has an active run" in error_message:
            active_run_id = error_message.split('run_')[1].split('.')[0]
            run = {'id': f'run_{active_run_id}', 'thread_id': thread_id}
            run_status = complete_run(run)
            log_message('info', f'Previously active run status: {run_status}')
            return make_request('POST', url, headers, data)
        else:
            raise e

def complete_run(run: Dict[str, Any]) -> Dict[str, Any]:
    """
    Completes a run by checking its status and handling any required actions.

    Args:
        run (Dict[str, Any]): The run object.

    Returns:
        Dict[str, Any]: The final status of the run.
    """
    thread_id = run['thread_id']
    run_id = run['id']
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_CONFIG['api_key']}",
        "OpenAI-Beta": "assistants=v2"
    }

    while True:
        run_status = make_request('GET', url, headers)
        status = run_status.get('status')

        if status == 'completed':
            log_message('info', f"Run {run_id} completed.")
            break
        elif status == 'failed':
            error_message = run_status.get('error', {}).get('message', 'Unknown error')
            error_type = run_status.get('error', {}).get('type', 'Unknown type')
            error_code = run_status.get('error', {}).get('code', 'Unknown code')
            detailed_message = (
                f"Run failed.\n"
                f"Error Message: {error_message}\n"
                f"Error Type: {error_type}\n"
                f"Error Code: {error_code}"
            )
            log_message('error', detailed_message)
            raise Exception(detailed_message)
        elif status == 'cancelled':
            log_message('error', f"Run {run_id} was cancelled.")
            raise Exception("Run was cancelled.")
        elif status == 'requires_action' and run_status['required_action']['type'] == 'submit_tool_outputs':
            submit_tool_outputs(run_status)
        else:
            time.sleep(0.5)

    return run_status

def submit_tool_outputs(run_status: Dict[str, Any]) -> None:
    """
    Submits tool outputs required to complete the run.

    Args:
        run_status (Dict[str, Any]): The current status of the run.
    """
    url = f"https://api.openai.com/v1/threads/{run_status['thread_id']}/runs/{run_status['id']}/submit_tool_outputs"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_CONFIG['api_key']}",
        "OpenAI-Beta": "assistants=v2"
    }

    tool_outputs = []
    tool_calls = run_status['required_action']['submit_tool_outputs']['tool_calls']
    for tool_call in tool_calls:
        tool_name = tool_call['function']['name']
        parameters = json.loads(tool_call['function']['arguments'])
        output = get_tool_output(tool_name, parameters)
        tool_outputs.append({
            "tool_call_id": tool_call['id'],
            "output": output
        })

    data = {
        "tool_outputs": tool_outputs
    }

    make_request('POST', url, headers, data)

def get_thread_messages(thread_id: str) -> Dict[str, Any]:
    """
    Retrieves the messages for the given thread ID.

    Args:
        thread_id (str): The thread ID.

    Returns:
        Dict[str, Any]: The messages associated with the thread ID.
    """
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_CONFIG['api_key']}",
        "OpenAI-Beta": "assistants=v2"
    }
    return make_request('GET', url, headers)
