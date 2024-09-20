# Pair programming, using few shots, nl, two samples:

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
    jsonl_filename = 'Result'
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
Requirement: prime_fib returns n-th number that is a Fibonacci number and it’s also prime.
'''
    content2 = '''
Driver:
def is_prime(n: int):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True
fib_seq = [1, 1]
counter = n
while counter > 0:
    fib_seq.append(fib_seq[-1] + fib_seq[-2])
    if is_prime(fib_seq[-1]):
        counter -= 1
return fib_seq[-1]
'''
    content3 = '''
Requirement: Create a function that takes integers, floats, or strings representing real numbers, and returns the larger variable in its given variable type. Return None if the values are equal. Note: If a real number is represented as a string, the floating point might be . or ,
'''
    content4 = '''
Driver:
def compare_one(a, b):
    a_original = a
    b_original = b
    if isinstance(a, str):
        a = float(a.replace(’,’, ’.’))
    if isinstance(b, str):
        b = float(b.replace(’,’, ’.’))
    if a > b:
        return a_original
    elif b > a:
        return b_original
    else:
        return None
'''
    messages = [
        {'role': 'system', 'content': f''},
        {'role': 'user', 'content': f"{content1}"},
        {'role': 'assistant', 'content': f'{content2}'},
        {'role': 'user', 'content': f"{content3}"},
        {'role': 'assistant', 'content': f'{content4}'},
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
Requirement: prime_fib returns n-th number that is a Fibonacci number and it’s also prime.
Driver:
def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False 
    i=5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True
def prime_fib(n):
    if n <= 0:
        raise ValueError("n must be a positive integer.")
    fib = [0, 1]  # Initial Fibonacci sequence
    count = 0  # Count of prime Fibonacci numbers
    while count < n:
        # Generate the next Fibonacci number
        next_fib = fib[-1] + fib[-2]
        # Check if the new Fibonacci number is prime
        if is_prime(next_fib):
            count += 1
        # Append the new Fibonacci number to the list
        fib.append(next_fib)
    return fib[-2]  # The last prime Fibonacci number
'''
    content2 = '''
Observer: 
After rigorous testing and inspection of the provided code, several issues have been identified that affect the correct functionality of the program: The function is_prime checks for prime numbers, but it returns True for 1 and this behavior deviates from the standard definition where 1 is not considered a prime number. In the function prime_fib, the starting Fibonacci sequence is [0, 1]. While technically correct, this could result in the function considering 0 as a potential prime Fibonacci number, which is incorrect. In the same function, the return statement returns the second-to-last element of the Fibonacci sequence (fib[-2]), which is not necessarily the nth prime Fibonacci number the function is supposed to return. The above-mentioned issues need to be addressed to ensure the correct execution of the program. After these issues are fixed, the code should correctly return the nth prime number in the Fibonacci sequence.
Modified Code:
def is_prime(n: int):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True
fib_seq = [1, 1]
counter = n
while counter > 0:
    fib_seq.append(fib_seq[-1] + fib_seq[-2])
    if is_prime(fib_seq[-1]):
        counter -= 1
return fib_seq[-1]
'''
    content3 = '''
Requirement: Create a function that takes integers, floats, or strings representing real numbers, and returns the larger variable in its given variable type. Return None if the values are equal. Note: If a real number is represented as a string, the floating point might be . or ,
Driver:
def compare_one(a, b):
    if a == b:
        return None
    if isinstance(a, str):
        a = float(a.replace(’,’, ’.’))
    if isinstance(b, str):
        b = float(b.replace(’,’, ’.’))
    if isinstance(a, int) and isinstance(b, int):
        return max(a, b)
    else:
        return float(max(a, b))
'''
    content4 = '''
Observer: 
The testing of the function ‘compare_one‘ in the provided code has revealed several significant issues: 1. The function does not appropriately handle the case where both inputs are equal. It returns ‘None‘ instead of returning the equal values. 2. The function doesn’t retain the original type of the inputs when they are both integers. It converts the maximum value to a float before returning, which could lead to incorrect type handling in further operations. 3. If the larger value was originally a string, the function returns a float or int rather than the original string. Fixing these issues should result in a function that correctly compares two values, converting strings to floats for comparison if necessary, and returning the larger value in its original form, or ‘None‘ if they are equal.
Modified Code:
def compare_one(a, b):
    a_original = a
    b_original = b
    if isinstance(a, str):
        a = float(a.replace(’,’, ’.’))
    if isinstance(b, str):
        b = float(b.replace(’,’, ’.’))
    if a > b:
        return a_original
    elif b > a:
        return b_original
    else:
        return None
'''
    messages = [
        {'role': 'system', 'content': f''},
        {'role': 'user', 'content': f'{content1}'},
        {'role': 'assistant', 'content': f'{content2}'},
        {'role': 'user', 'content': f'{content3}'},
        {'role': 'assistant', 'content': f'{content4}'},
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
