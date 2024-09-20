# Detail Tranditional, nl, using few shots, two samples:

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

def add_to_jsonl(task_id, input_text):
    jsonl_filename = 'Result/history.jsonl'
    try:
        with open(jsonl_filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        lines = []

    found = False
    for i, line in enumerate(lines):
        data = json.loads(line)
        if data['task_id'] == task_id:
            data['prompt'] += input_text
            lines[i] = json.dumps(data, ensure_ascii=False) + '\n'
            found = True
            break

    if not found:
        new_entry = {'task_id': task_id, 'prompt': input_text}
        lines.append(json.dumps(new_entry, ensure_ascii=False) + '\n')

    with open(jsonl_filename, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def get_analyst(prompt, task_id):
    content1 = '''
Requirement: Write a function to find the longest chain which can be formed from the given set of pairs.
'''
    content2 = '''
Plan:
Guidance for developers:
- The function should take a list of pairs as input.
- Carefully examine the examples to understand the requirements.
- It seems the goal is to find the longest chain of pairs.
- The chain must be formed by connecting pairs such that the second element of one pair matches the first element of the next pair.
- The function should return the length of the longest chain.

Steps to consider:
1. Check if the list of pairs is empty. If so, return 0.
2. Sort the list of pairs based on the second element of each pair.
3. Iterate through the sorted pairs and construct chains.
4. Keep track of the length of the longest chain encountered.
5. Return the length of the longest chain.

Please make sure to handle edge cases and test your function with additional cases.
'''
    content3 = '''
Requirement: Write a function to reverse words in a given string.
'''
    content4 = '''
Plan:
Guidance for Developers:
1. Function Signature:
    - Ensure the function signature matches the provided one (`def reverse_words(input_string):`).
2. Documentation:
    - Keep the docstring as it is, including the description and the examples.
3. Input Handling:
    - Confirm that the function handles input strings of various lengths and types.
    - Account for cases where the input string is empty (`""`).
4. Word Reversal Logic:
    - Implement the logic to reverse the words in the given string.
    - Consider removing leading and trailing whitespaces around words.
5. Testing:
    - Generate additional test cases to ensure the function handles a variety of scenarios.
    - Test with different input strings, including cases with multiple spaces between words.
    - Verify that the function works correctly with both short and long input strings.
6. Code Readability:
    - Write clean and readable code.
    - Use appropriate variable names and follow PEP 8 conventions.
7. Edge Cases:
    - Consider edge cases, such as strings with only one word or strings with numbers.
8. Efficiency:
    - Aim for an efficient solution but prioritize readability and correctness.
9. Submission:
    - Submit the code with appropriate comments explaining any non-trivial sections.
10. Reusability:
    - Ensure the function is designed to be reusable and can be easily integrated into other code.
'''
    messages = [
        {'role': 'system', 'content': f''},
        {'role': 'user', 'content': f"{content1}"},
        {'role': 'assistant', 'content': f'{content2}'},
        {'role': 'user', 'content': f"{content3}"},
        {'role': 'assistant', 'content': f'{content4}'},
        {'role': 'user', 'content': f'''
Requirement: {prompt}
Plan: 
'''}
    ]
    analyst_say = get_completion_from_messages(messages)

    add_to_jsonl(task_id, content1)
    add_to_jsonl(task_id, content2)
    add_to_jsonl(task_id, content3)
    add_to_jsonl(task_id, content4)
    add_to_jsonl(task_id, prompt)
    add_to_jsonl(task_id, 'Requirement: Plan: ')

    save_history(task_id, 'Plan', analyst_say)
    return analyst_say

def get_coder1(analyst_say, task_id):
    content1 = '''
Plan:
Guidance for developers:
- The function should take a list of pairs as input.
- Carefully examine the examples to understand the requirements.
- It seems the goal is to find the longest chain of pairs.
- The chain must be formed by connecting pairs such that the second element of one pair matches the first element of the next pair.
- The function should return the length of the longest chain.

Steps to consider:
1. Check if the list of pairs is empty. If so, return 0.
2. Sort the list of pairs based on the second element of each pair.
3. Iterate through the sorted pairs and construct chains.
4. Keep track of the length of the longest chain encountered.
5. Return the length of the longest chain.

Please make sure to handle edge cases and test your function with additional cases.
'''
    content2 = '''
Code:
def longest_chain(pairs):
    # Step 1: Check if the list of pairs is empty. If so, return 0.
    if not pairs:
        return 0

    # Step 2: Sort the list of pairs based on the second element of each pair.
    sorted_pairs = sorted(pairs, key=lambda x: x[1])

    # Step 3: Iterate through the sorted pairs and construct chains.
    longest_chain_length = 1  # Initialize with 1 as each pair forms a chain of length 1.
    current_chain_length = 1
    current_pair = sorted_pairs[0]

    for next_pair in sorted_pairs[1:]:
        # Step 4: Check if the next pair forms a chain with the current pair.
        if current_pair[1] == next_pair[0]:
            current_chain_length += 1
        else:
            # If the chain is broken, update the longest chain if needed and reset the current chain.
            longest_chain_length = max(longest_chain_length, current_chain_length)
            current_chain_length = 1
            current_pair = next_pair

    # Step 5: Return the length of the longest chain.
    return max(longest_chain_length, current_chain_length)
'''
    content3 = '''
Plan:
Guidance for Developers:
1. Function Signature:
    - Ensure the function signature matches the provided one (`def reverse_words(input_string):`).
2. Documentation:
    - Keep the docstring as it is, including the description and the examples.
3. Input Handling:
    - Confirm that the function handles input strings of various lengths and types.
    - Account for cases where the input string is empty (`""`).
4. Word Reversal Logic:
    - Implement the logic to reverse the words in the given string.
    - Consider removing leading and trailing whitespaces around words.
5. Testing:
    - Generate additional test cases to ensure the function handles a variety of scenarios.
    - Test with different input strings, including cases with multiple spaces between words.
    - Verify that the function works correctly with both short and long input strings.
6. Code Readability:
    - Write clean and readable code.
    - Use appropriate variable names and follow PEP 8 conventions.
7. Edge Cases:
    - Consider edge cases, such as strings with only one word or strings with numbers.
8. Efficiency:
    - Aim for an efficient solution but prioritize readability and correctness.
9. Submission:
    - Submit the code with appropriate comments explaining any non-trivial sections.
10. Reusability:
    - Ensure the function is designed to be reusable and can be easily integrated into other code.
'''
    content4 = '''
Code:
def reverse_words(input_string):
    """
    Reverse the order of words in a given string.

    Args:
    - input_string (str): The input string containing words to be reversed.

    Returns:
    - str: The input string with reversed words.
    
    Examples:
    >>> reverse_words("Hello World")
    'World Hello'
    
    >>> reverse_words("  Python is  fun  ")
    'fun is Python'
    
    >>> reverse_words("  ")
    ''
    """
    # Input handling
    if not input_string or not isinstance(input_string, str):
        return input_string

    # Split the input string into words
    words = input_string.split()

    # Reverse the order of words and join them into a new string
    reversed_string = ' '.join(words[::-1])

    return reversed_string

# Additional test cases
print(reverse_words("Hello World"))  # Output: 'World Hello'
print(reverse_words("  Python is  fun  "))  # Output: 'fun is Python'
print(reverse_words(""))  # Output: ''
print(reverse_words("OnlyOneWord"))  # Output: 'OnlyOneWord'
print(reverse_words("123 456 789"))  # Output: '789 456 123'
'''
    messages = [
        {'role': 'system', 'content': f''},
        {'role': 'user', 'content': f'{content1}'},
        {'role': 'assistant', 'content': f'{content2}'},
        {'role': 'user', 'content': f"{content3}"},
        {'role': 'assistant', 'content': f'{content4}'},
        {'role': 'user', 'content': f'''
Plan: {analyst_say}
Code: 
'''}]
    code_say = get_completion_from_messages(messages)

    add_to_jsonl(task_id, content1)
    add_to_jsonl(task_id, content2)
    add_to_jsonl(task_id, content3)
    add_to_jsonl(task_id, content4)
    add_to_jsonl(task_id, analyst_say)
    add_to_jsonl(task_id, 'Plan: Code: ')

    save_history(task_id, 'Coder1', code_say)
    result = extract_code_segments(code_say)
    save_history(task_id, 'Coder1', result)
    return result

def get_tester(prompt, code_say, task_id):
    content1 = '''
Requirement: Write a function to find the longest chain which can be formed from the given set of pairs.
Code:
def longest_chain(pairs):
    # Step 1: Check if the list of pairs is empty. If so, return 0.
    if not pairs:
        return 0

    # Step 2: Sort the list of pairs based on the second element of each pair.
    sorted_pairs = sorted(pairs, key=lambda x: x[1])

    # Step 3: Iterate through the sorted pairs and construct chains.
    longest_chain_length = 1  # Initialize with 1 as each pair forms a chain of length 1.
    current_chain_length = 1
    current_pair = sorted_pairs[0]

    for next_pair in sorted_pairs[1:]:
        # Step 4: Check if the next pair forms a chain with the current pair.
        if current_pair[1] == next_pair[0]:
            current_chain_length += 1
        else:
            # If the chain is broken, update the longest chain if needed and reset the current chain.
            longest_chain_length = max(longest_chain_length, current_chain_length)
            current_chain_length = 1
            current_pair = next_pair

    # Step 5: Return the length of the longest chain.
    return max(longest_chain_length, current_chain_length)
'''
    content2 = '''
Test Report:
The provided code appears to have a logical error in the section where the chain lengths are being updated. Specifically, in the loop where pairs are iterated, the condition to check if the next pair forms a chain with the current pair is incorrect. Additionally, there is a missing update for the longest chain length when the last pair forms a chain.
Here are the identified issues:
1. Logical Error in Chain Formation:
   - Code Snippet:
     ```python
     if current_pair[1] == next_pair[0]:
     ```
   - Issue:
     This condition checks if the second element of the current pair is equal to the first element of the next pair. However, the condition should check if the second element of the current pair is equal to the first element of the next pair. The correct condition should be:
     ```python
     if current_pair[1] == next_pair[0]:
     ```
2. Missing Update for Longest Chain Length:
   - Code Snippet:
     ```python
     longest_chain_length = max(longest_chain_length, current_chain_length)
     ```
   - Issue:
     The update for the longest chain length is missing when the loop ends. This update should be added after the loop to ensure that the length of the longest chain is correctly calculated even when the last pair forms a chain.
'''
    content3 = '''
Requirement: Write a function to reverse words in a given string.
Code:
def reverse_words(input_string):
    """
    Reverse the order of words in a given string.

    Args:
    - input_string (str): The input string containing words to be reversed.

    Returns:
    - str: The input string with reversed words.
    
    Examples:
    >>> reverse_words("Hello World")
    'World Hello'
    
    >>> reverse_words("  Python is  fun  ")
    'fun is Python'
    
    >>> reverse_words("  ")
    ''
    """
    # Input handling
    if not input_string or not isinstance(input_string, str):
        return input_string

    # Split the input string into words
    words = input_string.split()

    # Reverse the order of words and join them into a new string
    reversed_string = ' '.join(words[::-1])

    return reversed_string

# Additional test cases
print(reverse_words("Hello World"))  # Output: 'World Hello'
print(reverse_words("  Python is  fun  "))  # Output: 'fun is Python'
print(reverse_words(""))  # Output: ''
print(reverse_words("OnlyOneWord"))  # Output: 'OnlyOneWord'
print(reverse_words("123 456 789"))  # Output: '789 456 123'
'''
    content4 = '''
Test Report:
1. Requirement Violation:
   - The requirement specifies that the function should be named `reverse_words(input_string)`, but the provided code defines the function as `reverse_words_str(input_string)`. The function name does not match the requirement.
2. Requirement Violation:
   - The requirement examples include cases with leading and trailing spaces, but the code does not account for removing leading and trailing whitespaces around words.
3. Requirement Violation:
   - The requirement specifies a test case for an empty string (`reverse_words("")`), but the code does not handle this case correctly. The function returns the input string as is instead of an empty string.
4. Requirement Violation:
   - The requirement examples include cases with multiple spaces between words, but the code does not handle this scenario correctly. The output may have extra spaces.
5. Requirement Violation:
   - The requirement examples include cases with only one word, but the code does not handle this scenario correctly. The output may have leading/trailing spaces around the single word.
6. Requirement Violation:
   - The requirement examples include a case with numbers (`reverse_words("123 456 789")`), but the code does not handle this scenario correctly. The output may have leading/trailing spaces around the numbers.
7. Code Issue:
   - The code checks for input string emptiness with `if not input_string`, but this does not handle cases where the input string is a non-empty string that evaluates to `False` (e.g., `"0"`). It would be better to explicitly check for an empty string using `if input_string == ""`.
8. Code Issue:
   - The code returns the input string without reversing the words if the input is not a string. The requirement does not explicitly mention handling non-string inputs. Depending on the use case, it might be more appropriate to raise an exception for non-string inputs instead of returning the input as is.
9. Code Issue:
   - The code does not account for trailing spaces in the output. The requirement does not specify whether trailing spaces are allowed or not.
Recommendations for Modification:
   - Adjust the function name to match the requirement (`reverse_words`).
   - Update the logic to remove leading and trailing whitespaces around words.
   - Correctly handle cases with multiple spaces between words.
   - Ensure correct handling of input strings with only one word.
   - Address the issue with numbers in the input string.
   - Improve the handling of empty strings.
   - Consider whether trailing spaces in the output are acceptable.
   - Refine the input handling to better handle non-string inputs.
   - Explicitly check for an empty string using `if input_string == ""`.
'''
    messages = [
        {'role': 'system', 'content': f''},
        {'role': 'user', 'content': f'{content1}'},
        {'role': 'assistant', 'content': f'{content2}'},
        {'role': 'user', 'content': f"{content3}"},
        {'role': 'assistant', 'content': f'{content4}'},
        {'role': 'user', 'content': f'''
Requirement: {prompt}
Code: {code_say}
Test Report: 
'''}
]
    test_say = get_completion_from_messages(messages)
    
    add_to_jsonl(task_id, content1)
    add_to_jsonl(task_id, content2)
    add_to_jsonl(task_id, content3)
    add_to_jsonl(task_id, content4)
    add_to_jsonl(task_id, prompt)
    add_to_jsonl(task_id, code_say)
    add_to_jsonl(task_id, 'Requirement: Code: Test Report: ')

    save_history(task_id, 'Test Report', test_say)
    return test_say

def get_coder2(prompt, code_say, test_say, task_id):
    content1 = '''
Requirement: Write a function to find the longest chain which can be formed from the given set of pairs.
Code:
def longest_chain(pairs):
    # Step 1: Check if the list of pairs is empty. If so, return 0.
    if not pairs:
        return 0

    # Step 2: Sort the list of pairs based on the second element of each pair.
    sorted_pairs = sorted(pairs, key=lambda x: x[1])

    # Step 3: Iterate through the sorted pairs and construct chains.
    longest_chain_length = 1  # Initialize with 1 as each pair forms a chain of length 1.
    current_chain_length = 1
    current_pair = sorted_pairs[0]

    for next_pair in sorted_pairs[1:]:
        # Step 4: Check if the next pair forms a chain with the current pair.
        if current_pair[1] == next_pair[0]:
            current_chain_length += 1
        else:
            # If the chain is broken, update the longest chain if needed and reset the current chain.
            longest_chain_length = max(longest_chain_length, current_chain_length)
            current_chain_length = 1
            current_pair = next_pair

    # Step 5: Return the length of the longest chain.
    return max(longest_chain_length, current_chain_length)

# Testing the function with provided examples
print(longest_chain([(1, 2)]))                     # Output: 1
print(longest_chain([(1, 2), (2, 3), (3, 4)]))     # Output: 3
print(longest_chain([(1, 5), (2, 6), (3, 7), (4, 8)]))  # Output: 1
print(longest_chain([(5, 6), (2, 3), (1, 2), (4, 5)]))   # Output: 4
print(longest_chain([]))                           # Output: 0

Test Report:
The provided code appears to have a logical error in the section where the chain lengths are being updated. Specifically, in the loop where pairs are iterated, the condition to check if the next pair forms a chain with the current pair is incorrect. Additionally, there is a missing update for the longest chain length when the last pair forms a chain.
Here are the identified issues:
1. Logical Error in Chain Formation:
   - Code Snippet:
     ```python
     if current_pair[1] == next_pair[0]:
     ```
   - Issue:
     This condition checks if the second element of the current pair is equal to the first element of the next pair. However, the condition should check if the second element of the current pair is equal to the first element of the next pair. The correct condition should be:
     ```python
     if current_pair[1] == next_pair[0]:
     ```
2. Missing Update for Longest Chain Length:
   - Code Snippet:
     ```python
     longest_chain_length = max(longest_chain_length, current_chain_length)
     ```
   - Issue:
     The update for the longest chain length is missing when the loop ends. This update should be added after the loop to ensure that the length of the longest chain is correctly calculated even when the last pair forms a chain.
'''
    content2 = '''
Modified Code:
def longest_chain(pairs):
    if not pairs:
        return 0

    sorted_pairs = sorted(pairs, key=lambda x: x[1])

    longest_chain_length = 1
    current_chain_length = 1
    current_pair = sorted_pairs[0]

    for next_pair in sorted_pairs[1:]:
        if current_pair[1] == next_pair[0]:
            current_chain_length += 1
        else:
            longest_chain_length = max(longest_chain_length, current_chain_length)
            current_chain_length = 1
            current_pair = next_pair

    # Update the longest chain length after the loop
    longest_chain_length = max(longest_chain_length, current_chain_length)

    return longest_chain_length
'''
    content3 = '''
Requirement: Write a function to reverse words in a given string.
Code:
def reverse_words(input_string):
    """
    Reverse the order of words in a given string.

    Args:
    - input_string (str): The input string containing words to be reversed.

    Returns:
    - str: The input string with reversed words.
    
    Examples:
    >>> reverse_words("Hello World")
    'World Hello'
    
    >>> reverse_words("  Python is  fun  ")
    'fun is Python'
    
    >>> reverse_words("  ")
    ''
    """
    # Input handling
    if not input_string or not isinstance(input_string, str):
        return input_string

    # Split the input string into words
    words = input_string.split()

    # Reverse the order of words and join them into a new string
    reversed_string = ' '.join(words[::-1])

    return reversed_string

# Additional test cases
print(reverse_words("Hello World"))  # Output: 'World Hello'
print(reverse_words("  Python is  fun  "))  # Output: 'fun is Python'
print(reverse_words(""))  # Output: ''
print(reverse_words("OnlyOneWord"))  # Output: 'OnlyOneWord'
print(reverse_words("123 456 789"))  # Output: '789 456 123'

Test Report:
1. Requirement Violation:
   - The requirement specifies that the function should be named `reverse_words(input_string)`, but the provided code defines the function as `reverse_words_str(input_string)`. The function name does not match the requirement.
2. Requirement Violation:
   - The requirement examples include cases with leading and trailing spaces, but the code does not account for removing leading and trailing whitespaces around words.
3. Requirement Violation:
   - The requirement specifies a test case for an empty string (`reverse_words("")`), but the code does not handle this case correctly. The function returns the input string as is instead of an empty string.
4. Requirement Violation:
   - The requirement examples include cases with multiple spaces between words, but the code does not handle this scenario correctly. The output may have extra spaces.
5. Requirement Violation:
   - The requirement examples include cases with only one word, but the code does not handle this scenario correctly. The output may have leading/trailing spaces around the single word.
6. Requirement Violation:
   - The requirement examples include a case with numbers (`reverse_words("123 456 789")`), but the code does not handle this scenario correctly. The output may have leading/trailing spaces around the numbers.
7. Code Issue:
   - The code checks for input string emptiness with `if not input_string`, but this does not handle cases where the input string is a non-empty string that evaluates to `False` (e.g., `"0"`). It would be better to explicitly check for an empty string using `if input_string == ""`.
8. Code Issue:
   - The code returns the input string without reversing the words if the input is not a string. The requirement does not explicitly mention handling non-string inputs. Depending on the use case, it might be more appropriate to raise an exception for non-string inputs instead of returning the input as is.
9. Code Issue:
   - The code does not account for trailing spaces in the output. The requirement does not specify whether trailing spaces are allowed or not.
Recommendations for Modification:
   - Adjust the function name to match the requirement (`reverse_words`).
   - Update the logic to remove leading and trailing whitespaces around words.
   - Correctly handle cases with multiple spaces between words.
   - Ensure correct handling of input strings with only one word.
   - Address the issue with numbers in the input string.
   - Improve the handling of empty strings.
   - Consider whether trailing spaces in the output are acceptable.
   - Refine the input handling to better handle non-string inputs.
   - Explicitly check for an empty string using `if input_string == ""`.
'''
    content4 = '''
Modified Code:
def reverse_words(input_string):
    """
    Reverse the order of words in a given string.

    Args:
    - input_string (str): The input string containing words to be reversed.

    Returns:
    - str: The input string with reversed words.
    
    Examples:
    >>> reverse_words("Hello World")
    'World Hello'
    
    >>> reverse_words("  Python   is   awesome   ")
    'awesome is Python'
    
    >>> reverse_words("")
    ''
    
    >>> reverse_words("Programming")
    'Programming'
    
    >>> reverse_words("123 456 789")
    '789 456 123'
    """
    # Input handling
    if input_string == "":
        return ""

    if not isinstance(input_string, str):
        raise TypeError("Input must be a string.")

    # Split the input string into words, remove leading/trailing spaces
    words = [word.strip() for word in input_string.split()]

    # Reverse the order of words and join them into a new string
    reversed_string = ' '.join(words[::-1])

    return reversed_string

# Additional test cases
print(reverse_words("Hello World"))  # Output: 'World Hello'
print(reverse_words("  Python   is   awesome   "))  # Output: 'awesome is Python'
print(reverse_words(""))  # Output: ''
print(reverse_words("OnlyOneWord"))  # Output: 'OnlyOneWord'
print(reverse_words("123 456 789"))  # Output: '789 456 123'
'''
    messages = [
        {'role': 'system', 'content': f''},
        {'role': 'user', 'content': f'{content1}'},
        {'role': 'assistant', 'content': f'{content2}'},
        {'role': 'user', 'content': f"{content3}"},
        {'role': 'assistant', 'content': f'{content4}'},
        {'role': 'user', 'content': f'''
Requirement: {prompt}
Code: {code_say}
Test Report: {test_say}
Modified Code: 
'''}]
    code_say = get_completion_from_messages(messages)

    add_to_jsonl(task_id, content1)
    add_to_jsonl(task_id, content2)
    add_to_jsonl(task_id, content3)
    add_to_jsonl(task_id, content4)
    add_to_jsonl(task_id, prompt)
    add_to_jsonl(task_id, code_say)
    add_to_jsonl(task_id, test_say)
    add_to_jsonl(task_id, 'Requirement: Code: Test Report: Modified Code: ')

    save_history(task_id, 'Coder1', code_say)
    result = extract_code_segments(code_say)
    save_history(task_id, 'Coder1', result)
    return result

def code_generation(api_key, task_id, prompt):
    openai.api_key = api_key

    analyst_say = get_analyst(prompt, task_id)
    code_say = get_coder1(analyst_say, task_id)
    test_say = get_tester(prompt, code_say, task_id)
    code_say2 = get_coder2(prompt, code_say, test_say, task_id)
    save_to_jsonl(task_id, code_say2)