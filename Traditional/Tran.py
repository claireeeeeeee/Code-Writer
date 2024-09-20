# Only Tranditional:

import openai
import os
import json
import re

def save_to_jsonl(task_id, code_segments):
    data = {"task_id": task_id, "completion": code_segments}
    with open("Results", "a") as file:
        file.write(json.dumps(data) + "\n")

def save_test(task_id, code_segments):
    with open("History", "a") as file:
        file.write(code_segments)

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
    return '\n'.join(code_segments)

def extract_json_from_text(text):
    pattern = r'({[^{}]*?"description"[^{}]*?"severity"[^{}]*?"suggested_fix"[^{}]*?})'
    matches = re.findall(pattern, text, re.DOTALL)
    valid_jsons = []
    for match in matches:
        try:
            extracted_json = json.loads(match)
            if all(key in extracted_json for key in ["description", "severity", "suggested_fix"]):
                valid_jsons.append(extracted_json)
        except json.JSONDecodeError:
            continue
    return valid_jsons

def save_json_to_file(json_data, task_id):
    with open("History", "a") as file:
        for entry in json_data:
            entry_with_task_id = {"task_id": task_id, **entry}
            file.write(json.dumps(entry_with_task_id) + "\n")

def format_test_reports(input_list):
    formatted_reports = []
    for idx, data in enumerate(input_list, 1):
        description = data.get('description', '')
        severity = data.get('severity', '')
        suggested_fix = data.get('suggested_fix', '')
        report = (
            "{idx}. {description}"
            "The tester also gave solution suggestions: {suggested_fix}"
        ).format(idx=idx, description=description, severity=severity, suggested_fix=suggested_fix)
        formatted_reports.append(report)
    return '\n'.join(formatted_reports)

def get_completion_from_messages(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]

def get_analyst(system_message, prompt, task_id):
    analyst_description = f"""
I want you to act as an analyst \
on our development team. Analyze a user requirement.\
The user requirement will be provided between triple backticks (```),

Your role involves two primary responsibilities: \
1:Decompose User Requirements: decomposes the requirement x into \
several easy-to-solve subtasks that facilitate the division \
of functional units.

2:Develop High-Level Implementation Plan: Then, develops a high-level plan \
that outlines the major steps of the implementation.
"""
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"The requirement from users is {prompt}."},
        {'role': 'assistant', 'content': f"{analyst_description}"}
    ]
    analyst_say = get_completion_from_messages(messages)
    save_history(task_id, 'Analyst', analyst_say)
    return analyst_say

def get_coder1(system_message, analyst_say, task_id):
    coder_description = f"""
You are taking on the role of a coder \
within our development team. Depending on the input you receive, \
your task is distinct:

Task Based on Input:
# Requirement Analyst Plan:
You will receive a plan from a requirement analyst, \
develop Python code in line with the plan. \
Ensure your code is efficient, adheres to \
readability standards, and follows coding best practices.

Your main objectives are:
1. You adhere strictly to the feedback given in the test report.
2. The modifications do not change the core functionality of the code.
3. You provide an improved version of the provided code that \
considers the feedback on readability and maintainability.

Note: No need for explanations or comments on the code you develop.
"""
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"The Requirement Analyst Plan from analyst is {analyst_say}. Output in Python code format."},
        {'role': 'assistant', 'content': f"{coder_description}"}
    ]
    code_say = get_completion_from_messages(messages)
    save_history(task_id, 'Coder1', code_say)
    result = extract_code_segments(code_say)
    save_history(task_id, 'Coder1', result)
    return result

def get_tester(system_message, code_say, prompt, task_id):
    #If the code you receive passes your tests and no issues are identified, \
    #please write a conclusion "Code Test Passed" in this step \
    #instead of writing JSON formatted document. 
    tester_description = f"""
I'd like you to assume the role of a tester within \
our development team. When you receive code from a coder, \
you are responsible for the following three steps:

Step 1: Document Test Report
Generate a comprehensive test report assessing various code aspects, \
including but not limited to functionality, readability, and maintainability.

Step 2: Advocate for Model-Simulated Testing
Promote the use of a process where our machine learning model \
simulates the testing phase and produces test reports, \
thereby automating quality assessment.

Step 3: Issue Reporting in JSON Format
List all identified issues in a JSON formatted document. \
Each issue entry should contain three key-value pairs: \
'description' for issue details, 'severity' to indicate \
the level of urgency, and 'suggested_fix' to propose a solution. \

Step 4: Conclusion
If the code you receive passes your tests and no issues are identified, \
in other words, in Step 3, there is not output in your Issue Reporting in JSON Format, \
please write a conclusion "Code Test Passed" in this step. \
If there are problems that need to be corrected, \
please write a conclusion "Code Test Failed" in this step. \

All parts of your response should be separated by \
triple backticks to denote different sections.
"""
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"The requirement from users is {prompt} The code from the coder is {code_say}"},
        {'role': 'assistant', 'content': f"{tester_description}"}
    ]
    test_say = get_completion_from_messages(messages)
    save_history(task_id, 'Tester', test_say)
    return test_say

def get_coder2(system_message, test_say, code_say, task_id):
    extracted_data = extract_json_from_text(test_say)
    save_json_to_file(extracted_data, task_id)
    test_data = format_test_reports(extracted_data)
    save_test(task_id, test_data)

    coder_description = f"""
You are taking on the role of a coder \
within our development team. Depending on the input you receive, \
your task is distinct:

Task Based on Input:
# Tester's Test Report:
You will receive a detailed test report and \
its accompanying Python code from a tester, \
your main task is to revise or optimize the accompanying \
code based on the issues and feedback outlined in the test report.

Your main objectives are:
1. You need to address all concerns and issues identified in the test report.
2. The modifications do not change the core functionality of the code \
and make sure that any changes you make do not introduce new bugs into the system. 
3. You provide an improved version of the provided code that \
considers the feedback on readability and maintainability.

Note: No need for explanations or comments on the code you develop.
"""
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"The test report from tester is {test_data} And its accompanying Python code is {code_say}. Output in Python code format."},
        {'role': 'assistant', 'content': f"{coder_description}"}
    ]
    result_say = get_completion_from_messages(messages)
    save_history(task_id, "Code2", result_say)
    result = extract_code_segments(result_say)
    save_history(task_id, "Code2", result)
    return result

def code_generation(api_key, task_id, prompt):
    openai.api_key = api_key

    system_message = f"""There is a development team that \
includes a requirement analyst, a coder, and a quality tester. \
The team needs to develop programs that satisfy the requirements of \
the users. The different roles have different divisions of \
labor and need to cooperate with each others"""

    analyst_say = get_analyst(system_message, prompt, task_id)
    code_say = get_coder1(system_message, analyst_say, task_id)
    test_say = get_tester(system_message, code_say, prompt, task_id)
    code_say = get_coder2(system_message, test_say, code_say, task_id)
    save_to_jsonl(task_id, code_say)
