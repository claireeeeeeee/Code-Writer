# Loop for Detail Tranditional:

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
        temperature=0,
    )
    return response.choices[0].message["content"]

def get_analyst(entry_point, prompt, task_id):
    messages = [
        {'role': 'system', 'content': f"Our development team consists of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Every role has distinct responsibilities that need to be diligently executed for the successful completion of the project. I would like for you to take on the role of a project leader, your goal being to devise a high-level plan to manage. When you, as a project leader, develop a plan, you need to break it down into easy-to-solvable subtasks for functional units and develop a high-level plan outlining the major steps to implement. This plan will be handed over to developers so the output I need is just the plan, no actual code or anything else."},
        {'role': 'user', 'content': f"The requirement from users is {prompt}."},
        {'role': 'assistant', 'content': f"""
You should guide the developers based on this description, ensuring they understand the context and direction and pay attention to every detail of the requirements. Your role here is to provide oversight and guidance without immersing yourself in the intricacies of the code. Please do not provide test cases directly to developers. Regarding the testing requirements for developers, please let him generate test cases and test them himself.
"""}]
    analyst_say = get_completion_from_messages(messages)
    save_history(task_id, 'Analyst', analyst_say)
    return analyst_say

def get_coder1(analyst_say, task_id):
    messages = [
        {'role': 'system', 'content': f"Our development team consists of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Every role has distinct responsibilities that need to be diligently executed for the successful completion of the project. I would like for you to assume the role of a developer. As a core member of the team, you will receive detailed plans from the project leader during the workflow. While you as a developer are writing code that meets the requirements of the plan, you need to use Python to complete the requirements the plans of analysts, taking care to ensure that the code you write is efficient, readable, and follows best practices. The output I need is just a working code, no need to explain your code or other content."},
        {'role': 'user', 'content': f"The Requirement Analyst Plan from analyst is {analyst_say}. Output in Python code format."},
        {'role': 'assistant', 'content': f"""
Your goal is to follow the requirements and write Python code to satisfy its requirements and generate your own test cases to test whether your function is accurate. It is crucial to follow the function names and packages required in it. You also need to check the code to ensure it meets all the criteria specified in the requirement. Make sure to look for edge cases and try to break the code to ensure it's robust. This ensures consistency and a unified direction in the development process. When you write code, ensure your Python code:
1. Is efficient in terms of algorithmic complexity.
2. Is readable, making it easier for other team members to understand and, if necessary, modify.
3. Adheres to best practices of Python, including PEP 8 style guidelines.
"""}]
    code_say = get_completion_from_messages(messages)
    save_history(task_id, 'Coder1', code_say)
    result = extract_code_segments(code_say)
    save_history(task_id, 'Coder1', result)
    return result

def get_tester(code_say, prompt, task_id):
    #If the code you receive passes your tests and no issues are identified, \
    #please write a conclusion "Code Test Passed" in this step \
    #instead of writing JSON formatted document. 
    tester_description = f"""
Below is a comprehensive guide on what your responsibilities entail. 
1. Function Names and Signatures Check: Verify that the function names specified in the development requirements are correctly used.
2. Import Statements: Validate that all necessary packages are correctly imported as specified in the development plan.
3. Implementation Completeness: Ensure that all required functionalities are fully implemented, per the development plan.
4. Unit Test Execution: 
Use the unit tests provided in the requirements to verify the functionality of the code. Verify that the program works as expected and returns the correct results. Make sure your program handles unexpected input or error conditions gracefully. If there are any errors, please write them in your report.
5. Exception Handling:
Test how the program handles unexpected input or error conditions. Make sure it fails gracefully without sudden crashes. At this step, you can generate your own test cases. The test cases provided in the requirements may not fully cover all situations. To ensure exception handling, you need to account for as many exception inputs as possible in advance. If there are any errors, please write them in your report.
6. Detailed Code Quality Analysis:
Readability: Review the code for readability. Simple, clear code is easier to maintain and update in the future. Assess whether comments and documentation are sufficient and clear.
Maintainability: Gauge how maintainable the code is. Is it modular? Could it be easily extended or modified?
Scalability and Performance: Test the scalability of your code. How it performs under different conditions and it should be able to handle larger scales if needed.
Best Practices: Determine whether the code adheres to industry best practices. This includes the use of design patterns, following naming conventions, and efficient resource management.
7. If the code or the revised code has passed your tests, write a conclusion "Code Test Passed".
"""
    messages = [
        {'role': 'system', 'content': 'There is a development team composed of project leaders, developers, and quality assurance testers. The objective of the team is to develop a function that meets the needs of the users. Each role has its unique responsibilities and requires collaboration for successful execution. When you test the code as a tester on the development team, I want you to make suggestions on the code and record test reports covering various aspects such as functionality, readability, maintainability, etc. Your role involves not just identifying and reporting errors but also ensuring that the code aligns perfectly with our standards and requirements. Note that you need to check not only these but also other criteria that you feel need to be tested.'},
        {'role': 'user', 'content': f"The requirement from users is {prompt} The code from the coder is {code_say}"},
        {'role': 'assistant', 'content': f"{tester_description}"}
    ]
    test_say = get_completion_from_messages(messages)
    save_history(task_id, 'Tester', test_say)
    return test_say

def get_coder2(i, test_say, code_say, task_id):
    coder_description = f"""
Your task is to revise or optimize the existing code based on the issues and feedback outlined in the tester's report. Keep the following guidelines in mind:
1. Issue Resolution: Address all concerns and issues identified in the testing report.
2. Code Integrity: Make sure that any changes you make do not introduce new bugs into the system.
3. Performance: Be cautious not to degrade the performance of the code. Optimize where possible but not at the expense of functionality or accuracy.
4. You don't need to provide comments or explanations for the code changes you make.
"""
    messages = [
        {'role': 'system', 'content': 'As a core member of the team, you will receive the test report from tester during the workflow. When you as a developer make changes to your code, you use Python to make the changes requested by the tester, taking care to ensure that the code you write is efficient, readable, and follows best practices. The output I need is just a working code, no need to explain your code or anything.'},
        {'role': 'user', 'content': f"The test report from tester is {test_say} And its accompanying Python code is {code_say}. Output in Python code format."},
        {'role': 'assistant', 'content': f"{coder_description}"}
    ]
    result_say = get_completion_from_messages(messages)
    code2 = 'Coder'+str(i+2)
    save_history(task_id, code2, result_say)
    result = extract_code_segments(result_say)
    save_history(task_id, code2, result)
    return result

def code_generation(api_key, task_id, prompt, entry_point):
    openai.api_key = api_key

    analyst_say = get_analyst(entry_point, prompt, task_id)
    code_say = get_coder1(analyst_say, task_id)
    test_say = get_tester(code_say, prompt, task_id)

    i = 0
    if "Code Test Passed" in test_say:
        i = -1
            
    while 0 <= i <= 5:
        # Enter test_say, extract it in get_coder2 function, and then return the modified extracted code
        code_say = get_coder2(i, test_say, code_say, task_id)
        test_say = get_tester(code_say, prompt, task_id)
        #test_results = check_tester(test_say, task_id)
        if "Code Test Passed" in test_say:
            i = -1
        else: 
            i += 1
        if i >= 5:
            save_to_jsonl(task_id, code_say)
        
    save_to_jsonl(task_id, code_say)
