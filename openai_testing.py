import requests
import json
import time
from config import OPENAI_API_KEY

ASSISTANT_ID = "asst_FMoi1phnqp2yVc6eTpleb7Mu"

def create_thread():
    url = "https://api.openai.com/v1/threads"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    data = {
        "messages": [{
            "role": "user",
            "content": "you are a helpfull assistant"
        }]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def retrieve_thread(thread_id):
    url = f"https://api.openai.com/v1/threads/{thread_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def add_message(thread_id, content):
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    data = {
        "role": "user",
        "content": content
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def get_messages(thread_id):
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_assistant(assistant_id):
    url = f"https://api.openai.com/v1/assistants/{assistant_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def create_run(thread_id, assistant_id):
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }
    data = {
        "assistant_id": assistant_id
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def complete_run(thread_id, run_id):
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v2"
    }

    while True:
        status_response = requests.get(url, headers=headers)
        run_status = status_response.json()

        if run_status['status'] == 'completed':
            print("Run completed.")
            break
        elif run_status['status'] in ['failed', 'cancelled']:
            print(f"Run {run_status['status']}.")
            break
        else:
            print(f"Run status: {run_status['status']}. Waiting...")
            time.sleep(0.5)  # Wait before checking again

    return run_status

def main():
    # Create a new thread
    thread_response = create_thread()
    thread_id = thread_response['id']
    print(f"Thread created with ID: {thread_id}")

    # Add a message to the thread
    add_message(thread_id, "Whats Up?")

    # Create a run
    run_response = create_run(thread_id, ASSISTANT_ID)
    run_id = run_response['id']

    # Complete the run
    complete_run(thread_id, run_id)

    # Get and print messages from the thread
    messages_response = get_messages(thread_id)
    for message in messages_response['data']:
        for content_part in message["content"]:
            if content_part["type"] == "text":
                print(content_part["text"]["value"])

if __name__ == "__main__":
    main()




