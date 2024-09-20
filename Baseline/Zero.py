# Zero/Baseline

import openai
import os
import json
import re

def save_to_jsonl(task_id, code_segments):
    data = {"task_id": task_id, "completion": code_segments}
    with open("Results", "a") as file:
        file.write(json.dumps(data) + "\n")

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
        {'role': 'user', 'content': f"{prompt}"},
        {'role': 'assistant', 'content': ''}
    ]
    test_say = get_completion_from_messages(messages)
    save_to_jsonl(task_id, test_say)

    return test_say