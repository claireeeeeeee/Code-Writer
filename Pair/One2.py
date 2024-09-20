# Only pair programming (once pair programming)

import openai
import os
import json
import re

def save_to_jsonl(task_id, code_segments):
    data = {"task_id": task_id, "completion": code_segments}
    with open("Result/samples.jsonl", "a") as file:
        file.write(json.dumps(data) + "\n")

def save_history(key1, key2, plan_say):
    filename="History/history.jsonl"
    key = str(key1) + str(key2)
    data = {
        key: plan_say
    }
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')

def extract_code_segments(input_string):
    code_pattern = r'```python(.*?)```'
    code_segments = re.findall(code_pattern, input_string, re.DOTALL)
    return '\n'.join(code_segments)

def get_completion_from_messages(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=1,
    )
    return response.choices[0].message["content"]

def code_generation(api_key, task_id, prompt):
    openai.api_key = api_key
    i_say1 = f"""
While you as a driver are writing code, your goal is to follow the requirements write Python code to satisfy its requirements and generate your own test cases to test whether your function is accurate. Please carefully follow every detail in the requirements. It is crucial to follow the function names and packages required in it. You also need to check the code to ensure it meets all the criteria specified in the requirement. Make sure to look for edge cases and try to break the code to ensure it is robust. When writing your Python code, pay attention to the following: 
1. Efficiency: Optimize your code in terms of algorithmic complexity to ensure it runs efficiently. 
2. Readability: Write code that is easy for your team members to understand and potentially modify in the future.
3. Best Practices: Adhere to the best practices of Python programming, including compliance with PEP 8 style guidelines.
"""
    messages1 = [
        {'role': 'system', 'content': 'Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as a driver, write a program according to the requirement, and then hand it over to the observer for inspection.'},
        {'role': 'user', 'content': f'The requirement from users is {prompt}. Output in Python code format.'},
        {'role': 'assistant', 'content': f'{i_say1}'}
    ]
    analyst_say = get_completion_from_messages(messages1)
    save_history(task_id, 'Driver', analyst_say)

    i_say2 = f"""
Here is what you need to include: 
1. Code Inspection: Please check the code against the requirements received. Please make sure that the correct function name is used in the code and that all required functions in the requirements are implemented. 
2. Unit Test Execution: Use the provided unit tests from the requirements to validate the functionality of the code. Verify that the program works as expected and returns the correct results. You should also generate your own test cases to additionally test functions. Make sure your program handles unexpected input or error conditions gracefully. If there are any differences, please modify them in the final code.
3. Detailed Analysis: Beyond just the functionality, assess the code for readability. A clear and understandable code will be crucial for future maintenance and updates.You need to gauge the maintainability of the code. Consider factors like modularity, scalability, and whether best coding practices have been followed. 
4. Code Improvements: Improve the code provided to you based on your analysis reports to provide a final version of the code.
"""
    messages2 = [
        {'role': 'system', 'content': 'Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as an observer, review each line of code. '},
        {'role': 'user', 'content': f'The code written by the driver is {analyst_say}. And the requirements for it are {prompt}. Output in Python code format.'},
        {'role': 'assistant', 'content': f'{i_say2}'}
    ]

    code_say = get_completion_from_messages(messages2)
    save_history(task_id, 'Observer', code_say)

    messages2 = [
        {'role': 'system', 'content': 'Only output the final version of the code, and only the code(no any descriptions).'},
        {'role': 'user', 'content': f"The requirement is {prompt}. The report from the developer is {code_say}. "},
        {'role': 'assistant', 'content': f'Your objective is to extract the final version of the code for me, by reading the final report from the developer.  Please remember to remove the code used by the test, and only keep the Python functions needed in the requirements(mentioned in the function signature.). Please remember to provide only the final version of the code.'}
    ]

    i_say = get_completion_from_messages(messages2)
    save_history(task_id, 'Extract', i_say)

    save_to_jsonl(task_id, i_say)
