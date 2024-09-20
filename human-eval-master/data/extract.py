import json

def extract_no_examples_prompts(input_file, output_file):
    # Open the input file for reading
    with open(input_file, 'r', encoding='utf-8') as infile:
        # Open the output file for writing
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Iterate through each line in the input file
            for line in infile:
                try:
                    # Parse the line as a JSON object
                    json_object = json.loads(line)
                    prompt = json_object.get('prompt', None)

                    if prompt and '>>>' not in prompt:
                        # Write the original line to the output file
                        outfile.write(line)
                except json.JSONDecodeError:
                    # If parsing fails, print an error and continue
                    print(f'Error parsing line: {line}')

import json

def filter_prompts(input_file, output_file):
    # Open the input file for reading
    with open(input_file, 'r', encoding='utf-8') as infile:
        # Open the output file for writing
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Iterate through each line in the input file
            for line in infile:
                try:
                    # Parse the line as a JSON object
                    json_object = json.loads(line)
                    # Get the 'prompt' field from the JSON object
                    prompt = json_object.get('prompt', None)
                    # Check if '>>>' is in the 'prompt' field
                    if prompt and '>>>' not in prompt:
                        # Write the original line to the output file
                        outfile.write(line)
                except json.JSONDecodeError:
                    # If parsing fails, print an error and continue
                    print(f'Error parsing line: {line}')

# Specify the input and output file paths
input_file_path = '/Users/claire/Desktop/report/human-eval-master/data/HumanEval.jsonl'
output_file_path = '/Users/claire/Desktop/report/human-eval-master/data/HumanEval_output.jsonl'

#extract_no_examples_prompts(input_file_path, output_file_path)

filter_prompts(input_file_path, output_file_path)