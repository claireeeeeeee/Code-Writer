# Pair programming, using few shots, two samples:

import openai
import os
import json
import re

def save_to_jsonl(task_id, code_segments):
    data = {"task_id": task_id, "completion": code_segments}
    with open("Result", "a") as file:
        file.write(json.dumps(data) + "\n")

def save_history(key1, key2, plan_say):
    filename="History"
    key = str(key1) + str(key2)
    data = {
        key: plan_say
    }
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')

def extract_code_segments(input_string):
    code_pattern = r'```python(.*?)```'
    code_segments = re.findall(code_pattern, input_string, re.DOTALL)
    if not code_segments:
        return input_string
    return '\n'.join(code_segments)

def add_to_jsonl(task_id, input_text):
    jsonl_filename = '/Users/claire/Desktop/report/Interface/Result/history_25.jsonl'
    try:
        with open(jsonl_filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        lines = []

    # Check if the same task ID exists
    found = False
    for i, line in enumerate(lines):
        data = json.loads(line)
        if data['task_id'] == task_id:
            # If the same task ID exists, update the corresponding prompt
            data['prompt'] += input_text
            lines[i] = json.dumps(data, ensure_ascii=False) + '\n'
            found = True
            break

    # If the same task ID does not exist, add a new record
    if not found:
        new_entry = {'task_id': task_id, 'prompt': input_text}
        lines.append(json.dumps(new_entry, ensure_ascii=False) + '\n')

    # Write the updated data back to the file
    with open(jsonl_filename, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def get_completion_from_messages(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]

def get_coder(prompt, task_id):
    content1 = '''
Requirement: def longest_chain(pairs):\n    \"\"\" Write a function to find the longest chain which can be formed from the given set of pairs.\n    >>> longest_chain([(1, 2)])\n    1\n    >>> longest_chain([(1, 2), (2, 3), (3, 4)])\n    3\n    >>> longest_chain([(1, 5), (2, 6), (3, 7), (4, 8)])\n    1\n    >>> longest_chain([(5, 6), (2, 3), (1, 2), (4, 5)])\n    4\n    >>> longest_chain([])\n    0\n    \"\"\"\n
'''
    content2 = '''
Driver:
def longest_chain(pairs):
    pairs.sort(key=lambda x: x[1])  # Sort the pairs based on the second element

    n = len(pairs)
    dp = [1] * n

    for i in range(1, n):
        for j in range(i):
            if pairs[i][0] > pairs[j][1] and dp[i] < dp[j] + 1:
                dp[i] = dp[j] + 1

    max_length = max(dp)
    return max_length
'''
    content3 = '''
Requirement: def reverse_words(input_string):\n    \"\"\" Write a function to reverse words in a given string.\n    >>> reverse_words("Hello World")\n    World Hello\n    >>> reverse_words("   Python   is   awesome   ")\n    awesome is Python\n    >>> reverse_words("")\n    \n    >>> reverse_words("Programming")\n    Programming\n    >>> reverse_words("123 456 789")\n    789 456 123\n    \"\"\"\n
'''
    content4 = '''
Driver:
def reverse_words(input_string):
    # Split the string into a list of words
    words = input_string.split()

    # Reverse the order of words
    reversed_words = words[::-1]

    # Join the reversed words back into a string
    reversed_string = ' '.join(reversed_words)

    return reversed_string
'''
    messages = [
        {'role': 'system', 'content': f''},
        {'role': 'user', 'content': f"{content1}"},
        {'role': 'assistant', 'content': f'{content2}'},
        {'role': 'user', 'content': f"Requirement: {prompt}"}
    ]
    analyst_say = get_completion_from_messages(messages)
    save_history(task_id, 'Driver1', analyst_say)
    result = extract_code_segments(analyst_say)
    save_history(task_id, 'Code1', result)

    add_to_jsonl(task_id, content1)
    add_to_jsonl(task_id, content2)
    add_to_jsonl(task_id, prompt)
    return result

def get_tester(prompt, analyst_say, task_id):
    content1 = '''
Requirement: def longest_chain(pairs):\n    \"\"\" Write a function to find the longest chain which can be formed from the given set of pairs.\n    >>> longest_chain([(1, 2)])\n    1\n    >>> longest_chain([(1, 2), (2, 3), (3, 4)])\n    3\n    >>> longest_chain([(1, 5), (2, 6), (3, 7), (4, 8)])\n    1\n    >>> longest_chain([(5, 6), (2, 3), (1, 2), (4, 5)])\n    4\n    >>> longest_chain([])\n    0\n    \"\"\"\n
Driver:
def longest_chain(pairs):
    pairs.sort(key=lambda x: x[1])  # Sort the pairs based on the second element

    n = len(pairs)
    dp = [1] * n

    for i in range(1, n):
        for j in range(i):
            if pairs[i][0] > pairs[j][1] and dp[i] < dp[j] + 1:
                dp[i] = dp[j] + 1

    max_length = max(dp)
    return max_length
'''
    content2 = '''
Observer: 
It seems the provided code doesn't handle the case when the list of pairs is empty, leading to a `ValueError` when trying to find the maximum of an empty sequence.
Modified Code:
def longest_chain(pairs):
    if not pairs:
        return 0

    pairs.sort(key=lambda x: x[1])  # Sort the pairs based on the second element

    n = len(pairs)
    dp = [1] * n

    for i in range(1, n):
        for j in range(i):
            if pairs[i][0] > pairs[j][1] and dp[i] < dp[j] + 1:
                dp[i] = dp[j] + 1

    max_length = max(dp)
    return max_length
'''
    content3 = '''
Requirement: def reverse_words(input_string):\n    \"\"\" Write a function to reverse words in a given string.\n    >>> reverse_words("Hello World")\n    World Hello\n    >>> reverse_words("   Python   is   awesome   ")\n    awesome is Python\n    >>> reverse_words("")\n    \n    >>> reverse_words("Programming")\n    Programming\n    >>> reverse_words("123 456 789")\n    789 456 123\n    \"\"\"\n
Driver:
def reverse_words(input_string):
    # Split the string into a list of words
    words = input_string.split()

    # Reverse the order of words
    reversed_words = words[::-1]

    # Join the reversed words back into a string
    reversed_string = ' '.join(reversed_words)

    return reversed_string
'''
    content4 = '''
Observer: 
The code seems to work correctly, however one potential improvement is to handle cases where the input string contains leading or trailing spaces. We can modify the code to remove leading and trailing spaces before splitting the string. 
Modified Code:
def reverse_words(input_string):
    # Remove leading and trailing spaces
    input_string = input_string.strip()

    # Split the string into a list of words
    words = input_string.split()

    # Reverse the order of words
    reversed_words = words[::-1]

    # Join the reversed words back into a string
    reversed_string = ' '.join(reversed_words)

    return reversed_string
'''
    messages = [
        {'role': 'system', 'content': f''},
        {'role': 'user', 'content': f'{content1}'},
        {'role': 'assistant', 'content': f'{content2}'},
        {'role': 'user', 'content': f'''
Requirement: {prompt}
Driver: {analyst_say}
'''}
    ]
    code_say = get_completion_from_messages(messages)
    
    add_to_jsonl(task_id, content1)
    add_to_jsonl(task_id, content2)
    add_to_jsonl(task_id, analyst_say)
    add_to_jsonl(task_id, prompt)

    save_history(task_id, 'Observer', code_say)
    return code_say

def get_coder2(prompt, test_say, task_id):
    coder_description = f'''
Your objective is to extract the final version of the code for me, by reading the final report from the developer.  Please remember to remove the code used by the test, and only keep the Python functions needed in the requirements(mentioned in the function signature.). Please remember: provide only the final version of the code.
'''
    messages = [
        {'role': 'system', 'content': f"{coder_description}"},
        {'role': 'user', 'content': f"Here is the requirement: {prompt} and the final report from the developer: {test_say}."}
    ]
    result_say = get_completion_from_messages(messages)
    save_history(task_id, 'Extract', result_say)
    result = extract_code_segments(result_say)

    add_to_jsonl(task_id, test_say)
    add_to_jsonl(task_id, prompt)
    add_to_jsonl(task_id, coder_description)
    add_to_jsonl(task_id, 'Here is the requirement: and the final report from the developer:')
    
    return result
    
def code_generation(api_key, txt):
    openai.api_key = api_key
    data=[]
    with open(txt, 'r', encoding='utf-8') as file:
        for line in file:
            data.append(json.loads(line.strip()))

    for a in data:
        task_id = a["task_id"]
        prompt = a["prompt"]
        
        code_say = get_coder(prompt, task_id)
        test_say = get_tester(prompt, code_say, task_id)
        result = get_coder2(prompt, test_say, task_id)
        save_to_jsonl(task_id, result)
