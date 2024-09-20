# Pair for Loop:

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

def get_completion_from_messages(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.5,
    )
    return response.choices[0].message["content"]

def get_coder(prompt, task_id):
    messages = [
        {'role': 'system', 'content': f"Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as a driver, write a program according to the requirement, and then hand it over to the observer for inspection."},
        {'role': 'user', 'content': f"The requirement from users is {prompt}."},
        {'role': 'assistant', 'content': f'''
While you as a driver are writing code, you need to write a Python function that meets a specific requirement, taking care to ensure that your code is efficient, readable, and follows best practices. Your goal is to follow the requirements write Python code to satisfy its requirements and generate your own test cases to test whether your function is accurate.  
This requirement will have: 
1. Package/Module: You may use any relevant Python packages or modules as required. 
2. Function Name: You must implement the function name.
3. Parameters: The function should accept specific types and numbers of parameters as indicated in the requirement. 
4. Function Description: Your task is to implement the function according to the provided requirement. Ensure that your code meets the specified criteria, and consider edge cases to ensure its robustness.
5. Attention to details: Please carefully follow every detail in the requirements.
6. Testing: Generate your own test cases to validate the function's accuracy and reliability.
It is crucial to follow the function names and packages required in it. You also need to check the code to ensure it meets all the criteria specified in the requirement. Make sure to look for edge cases and try to break the code to ensure it is robust. When writing your Python code, pay attention to the following: 
1. Efficiency: Optimize your code in terms of algorithmic complexity to ensure it runs efficiently. 
2. Readability: Write code that is easy for your team members to understand and potentially modify in the future.
3. Best Practices: Adhere to the best practices of Python programming, including compliance with PEP 8 style guidelines.
'''}]
    analyst_say = get_completion_from_messages(messages)
    save_history(task_id, 'Driver1', analyst_say)
    result = extract_code_segments(analyst_say)
    save_history(task_id, 'Code1', result)
    return result

def get_tester(prompt, analyst_say, task_id):
    messages = [
        {'role': 'system', 'content': f"Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as an observer, review each line of code. When you test the code, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Your role involves not just identifying and reporting errors but also ensuring that the code aligns perfectly with our standards and requirements. Note that you need to check not only these but also other criteria that you feel need to be tested."},
        {'role': 'user', 'content': f"The is code written by the driver is {analyst_say}. And the requirement is {prompt}"},
        {'role': 'assistant', 'content': f'''
Here is what you need to include (not the format or steps you have to follow): 
1. Code Inspection: Please check the code against the requirements received. Please make sure that the function name used in the code is correct and that all required functions in the requirements are implemented. 
2. Unit Test Execution: Use the provided unit tests from the requirements to validate the functionality of the code. Verify that the program works as expected and returns the correct results. You should also generate your own test cases to additionally test functions. Make sure your program handles unexpected input or error conditions gracefully. If there are any differences, please modify them in the final code.
3. Detailed Analysis: Beyond just the functionality, assess the code for readability. A clear and understandable code will be crucial for future maintenance and updates.You need to gauge the maintainability of the code. Consider factors like modularity, scalability, and whether best coding practices have been followed. 
4. Code Improvements: Improve the code provided to you based on your analysis reports to provide a final version of the code. If the original code can pass the test, that is, there is no need to modify the code, please write the conclusion "Code test passed."
'''}
    ]
    code_say = get_completion_from_messages(messages)
    save_history(task_id, 'Observer', code_say)
    return code_say

def get_coder2(i, test_say, code_say, task_id):
    coder_description = f"""
Your task is to revise or optimize the existing code based on the issues and feedback outlined in the tester's report. Keep the following guidelines in mind:
1. Issue Resolution: Address all concerns and issues identified in the testing report.
2. Code Integrity: Make sure that any changes you make do not introduce new bugs into the system.
3. Performance: Be cautious not to degrade the performance of the code. Optimize where possible but not at the expense of functionality or accuracy.
4. You don't need to provide comments or explanations for the code changes you make.
"""
    messages = [
        {'role': 'system', 'content': 'Pair programming is a software development approach in which two programmers collaborate at the same computer. The driver writes code, while the observer analyses each line of code as it is entered. Now you need to act as a driver, write a program according to the requirement, and then hand it over to the observer for inspection.'},
        {'role': 'user', 'content': f"The test report from Observer is {test_say} And its accompanying Python code is {code_say}. Output in Python code format."},
        {'role': 'assistant', 'content': f"{coder_description}"}
    ]
    result_say = get_completion_from_messages(messages)
    code2 = 'Driver'+str(i+2)
    code3 = 'Code'+str(i+2)
    save_history(task_id, code2, result_say)
    result = extract_code_segments(result_say)
    save_history(task_id, code3, result)
    return result
    
def code_generation(api_key, task_id, prompt, entry_point):
    openai.api_key = api_key

    code_say = get_coder(prompt, task_id)
    test_say = get_tester(prompt, code_say, task_id)

    i = 0
    if "CodeTestPassed" or "codetesthaspassed" or "codetestispassed" in test_say.lower().replace(" ", ""):
        i = -1

    while 0 <= i <= 5:
        # Enter test_say, extract it in get_coder2 function, and then return the modified extracted code
        code_say = get_coder2(i, test_say, code_say, task_id)
        test_say = get_tester(prompt, code_say, task_id)
        #test_results = check_tester(test_say, task_id)
        if "Code Test Passed" in test_say.lower():
            i = -1
        else: 
            i += 1
        if i >= 5:
            save_to_jsonl(task_id, code_say)
        
    save_to_jsonl(task_id, code_say)
