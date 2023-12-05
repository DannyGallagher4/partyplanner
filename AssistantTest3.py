import json
from flask import Flask, render_template, request
import openai
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
import gptParse

app = Flask(__name__)

GPT_MODEL = "gpt-4-1106-preview"

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + "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",
    }
    json_data = {"model": model, "messages": messages}
    if tools is not None:
        json_data.update({"tools": tools})
    if tool_choice is not None:
        json_data.update({"tool_choice": tool_choice})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def add_numbers(num1, num2):
    return num1+num2

def multply_numbers(num1, num2):
    return num1*num2

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "adds together 2 numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "num1": {
                        "type": "integer",
                        "description": "the first number to be added",
                    },
                    "num2": {
                        "type": "integer",
                        "description": "the second number to be added",
                    },
                },
                "required": ["num1", "num2"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "multiply_numbers",
            "description": "multiples together 2 numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "num1": {
                        "type": "integer",
                        "description": "the first number to be multiplied",
                    },
                    "num2": {
                        "type": "integer",
                        "description": "the second number to be multipled",
                    },
                },
                "required": ["num1", "num2"],
            },
        }
    }
]

history = []
messages = []

def parse_user_input(prompt):
    # outputs a list
    return gptParse.parse_request(prompt)

@app.route('/', methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        prompt = request.form['prompt']
        output = ""
        try:
            # Split the prompt to handle different types of queries
            queries = parse_user_input(prompt)

            for query in queries:
                if query == '':
                    continue
                messages.append({"role": "system", "content": "You are a general purpose AI, but know how to do addition and subtraction. Make sure to output both function calls and text. Try to make the text not much longer than 3 or 4 sentences if possible. Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
                messages.append({"role": "user", "content": query})
                chat_response = chat_completion_request(
                    messages, tools=tools
                )
                assistant_message = chat_response.json()["choices"][0]["message"]
                messages.append(assistant_message)
                if assistant_message["content"] != None:
                    print("AI: " + str(assistant_message["content"]))
                    output += str(assistant_message["content"]) + "\n"
                if "tool_calls" in assistant_message and assistant_message["tool_calls"]:
                    # Iterate through tool_calls to find add_numbers function call
                    for tool_call in assistant_message["tool_calls"]:
                        if tool_call["type"] == "function" and tool_call["function"]["name"] == "add_numbers":
                            # Extract and print the result
                            arguments = json.loads(tool_call["function"]["arguments"])
                            result = add_numbers(arguments["num1"], arguments["num2"])

                            tool_response = {
                                "role": "tool",
                                "name": "add_numbers",
                                "content": f"The result of addition is {result}",
                                "tool_call_id": tool_call["id"],
                            }
                            messages.append(tool_response)
                            print(f"AI: {result}")
                            output += tool_response["content"]+"\n"

                        elif tool_call["type"] == "function" and tool_call["function"]["name"] == "multiply_numbers":
                            # Extract and print the result
                            arguments = json.loads(tool_call["function"]["arguments"])
                            result = multply_numbers(arguments["num1"], arguments["num2"])

                            tool_response = {
                                "role": "tool",
                                "name": "multiply_numbers",
                                "content": f"The result of multiplication is {result}",
                                "tool_call_id": tool_call["id"],
                            }
                            messages.append(tool_response)
                            print(f"AI: {result}")
                            output += tool_response["content"]+"\n"
            history.append((prompt, output))
        except Exception as e:
                print(f"An error occurred: {e}")
        
    return render_template('index.html', history=history)

if __name__ == '__main__':
    app.run(debug=True)