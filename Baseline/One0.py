# coder only

import openai
import os
import json
import re

def save_to_jsonl(task_id, code_segments):
    data = {"task_id": task_id, "completion": code_segments}
    with open("Result", "a") as file:
        file.write(json.dumps(data) + "\n")

def extract_code_segments(input_string):
    code_pattern = r'```python(.*?)```'
    code_segments = re.findall(code_pattern, input_string, re.DOTALL)
    return '\n'.join(code_segments)

def get_completion_from_messages(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]

def code_generation(api_key, task_id, prompt):
    openai.api_key = api_key
    messages = [
        {'role': 'system', 'content': ''},
        {'role': 'user', 'content': f"The requirement from users is {prompt}."},
        {'role': 'assistant', 'content': 'Your task is to write the Python function implementing the above functionality. No need for explanations or comments on the code you develop.'}
    ]
    i_say = get_completion_from_messages(messages)
    save_to_jsonl(task_id, i_say)