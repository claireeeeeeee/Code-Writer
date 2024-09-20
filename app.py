from flask import Flask, render_template, request, jsonify
import openai
import os
import json
import re
import jsonlines
import pandas as pd

import time
from Baseline.Zero import code_generation as zero
from Baseline.One0 import code_generation as coder
from Traditional.Tran import code_generation as tran
from Pair.One2 import code_generation as pair
from Pair.Pairs import code_generation as pairs

from Traditional.Simple import code_generation as simple
from Traditional.Detail0 import code_generation as detail
from Traditional.Details import code_generation as details

from few.Detail_few import code_generation as detail_few
from few.Detail_few_nl import code_generation as detail_few_nl
from few.Pairs_few import code_generation as pairs_few
from few.Pairs_few_nl import code_generation as pairs_few_nl

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_text', methods=['POST'])
def process_text():
    user_input_path = request.form['user_input_path'] 
    kind = request.form['user_id'] 

    try:
        df = pd.read_csv(user_input_path)
        results = []
        for index, row in df.iterrows():
            user_input = row['prompt']
            task_id = row['task_id']
            result = process_text_helper(user_input, task_id, kind)
            results.append(result)

        final_result = "\n".join(results)
        processed_text = process_text_slowly(final_result)
        return jsonify({'result': processed_text})

    except Exception as e:
        return jsonify({'error': str(e)})

def process_text_helper(user_input, task_id, kind):
    openai.api_key = ""
    print(f"Debug: user_input={user_input}, task_id={task_id}, kind={kind}")
    if kind == "Zero (Baseline)":
        return zero(openai.api_key, task_id, user_input)
    elif kind == "Coder only":
        return coder(openai.api_key, task_id, user_input)
    elif kind == "Only tran":
        return tran(openai.api_key, task_id, user_input)
    elif kind == "Only pair programming":
        return pair(openai.api_key, task_id, user_input)
    elif kind == "Detail Tranditional":
        return detail(openai.api_key, task_id, user_input)
    elif kind == "Loop for Simple Tranditional":
        return simple(openai.api_key, task_id, user_input)
    elif kind == "Loop for Detail Tranditional":
        return details(openai.api_key, task_id, user_input)
    elif kind == "Loop for Pair programming":
        return pairs(openai.api_key, task_id, user_input)
    elif kind == "Few-shots: Pair programming":
        return pairs_few(openai.api_key, task_id, user_input)
    elif kind == "Few-shots: Pair programming & nl":
        return pairs_few_nl(openai.api_key, task_id, user_input)
    elif kind == "Few-shots: Tranditional":
        return detail_few(openai.api_key, task_id, user_input)
    elif kind == "Few-shots: Tranditional & nl":
        return detail_few_nl(openai.api_key, task_id, user_input)
    else:
        return "Invalid kind selected"

@app.route('/read_file', methods=['GET'])
def read_file():
    user_input_path = request.args.get('user_input_path', '')

    try:
        result = []

        with jsonlines.open(user_input_path) as reader:
            for line in reader.iter():
                result.append(line)

        return jsonify(result)

    except Exception as e:
        print(f"Error reading file: {e}")
        return jsonify({"error": f"Error reading file: {e}"}), 500 

def process_text_slowly(text):
    result = ""
    for char in text:
        result += char
        #time.sleep(0.1)  # Adjust the sleep duration based on your preference

    #result = result + "\n"
    return result

if __name__ == '__main__':
    app.run(debug=True)