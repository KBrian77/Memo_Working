import json
import requests
import datetime

stream = False

url = "https://chat.tune.app/api/chat/completions"
headers = {
    "Authorization": "tune-4d4a407b-ea73-4f3d-a288-a0de5db14d851709018521",
    "Content-Type": "application/json"
}

def process_response(response):
    chat_history = []
    assistant_response = ""
    if stream:
        for line in response.iter_lines():
            if line:
                l = line[6:]
                if l != b'[DONE]':
                    message = json.loads(l)
                    content = message.get('content')
                    if content.startswith('A:'):
                        assistant_response = content[3:]
                    else:
                        chat_history.append({
                            'role': 'user',
                            'content': content,
                            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')
                        })
    else:
        response_json = response.json()
        choices = response_json.get('choices')
        if choices:
            for choice in choices:
                message = choice.get('message')
                if message:
                    content = message.get('content')
                    if message.get('role') == 'assistant':
                        assistant_response = content
                    else:
                        chat_history.append({
                            'role': 'user',
                            'content': content,
                            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')
                        })
    return chat_history, assistant_response

chat_history = []

while True:
    with open("prompt.txt", "r") as file:
        system_prompt = file.read().strip()

    user_input = input("You: ")
    if user_input.strip().lower() == 'e':
        break

    data = {
        "temperature": 0.5,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        "model": "goliath-120b-16k-gptq",
        "stream": stream,
        "max_tokens": 1000
    }
    response = requests.post(url, headers=headers, json=data)
    user_messages, assistant_response = process_response(response)
    chat_history.extend(user_messages)
    print("Assistant:", assistant_response)

with open('chat_history.json', 'w') as f:
    json.dump(chat_history, f, indent=4)

print(chat_history
