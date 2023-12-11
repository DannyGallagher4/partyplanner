import json
from flask import Flask, render_template, request, jsonify, redirect
import openai
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
from urllib.parse import unquote, quote

mapbox_access_token = 'pk.eyJ1Ijoia2xvZGFuIiwiYSI6ImNscG16cXFrMjAxaW8ya29pbHM3ejI4bXAifQ.vfQJewHUm3kngAd22BCjoQ'

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

def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "tool": "magenta",
    }
    
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "tool":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))

def add_numbers(num1, num2):
    return num1+num2

def multply_numbers(num1, num2):
    return num1*num2

def go_somewhere(place_name):
    geocoding_url = f'https://api.mapbox.com/geocoding/v5/mapbox.places/{place_name}.json?access_token={mapbox_access_token}'
    response = requests.get(geocoding_url)
    data = response.json()

    if 'features' in data and data['features']:
        # Extract the coordinates from the first result
        coordinates = data['features'][0]['center']
        name = data['features'][0]['text']
        lnglatname = {'lng': coordinates[0], 'lat': coordinates[1], 'name': name}
    else:
        lnglatname = {'error': 'Place not found'}
    
    return lnglatname

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
            "description": "multiplies together 2 numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "num1": {
                        "type": "integer",
                        "description": "the first number to be multiplied",
                    },
                    "num2": {
                        "type": "integer",
                        "description": "the second number to be multiplied",
                    },
                },
                "required": ["num1", "num2"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "go_somewhere",
            "description": "takes a place name and uses the mapbox api to get the coordinates and exact name of that place",
            "parameters": {
                "type": "object",
                "properties": {
                    "place_name": {
                        "type": "string",
                        "description": "the inputted name of where the to go on the map",
                    }
                },
                "required": ["place_name"],
            },
        }
    }
]

history = []
messages = []

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('mapAIindex.html', history=history)
    
@app.route('/callAI', methods=["GET", "POST"])
def callAI():
    if request.method == 'POST':
        prompt = unquote(request.form['prompt'])
        output = ""
        data_to_return = ""
        isMap = False
        try:
            messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
            messages.append({"role": "user", "content": prompt})
            chat_response = chat_completion_request(
                messages, tools=tools
            )
            print(chat_response.json())
            assistant_message = chat_response.json()["choices"][0]["message"]
            print("1")
            messages.append(assistant_message)
            print("2")
            output = ""
            if assistant_message["content"] != None:
                print("AI: " + str(assistant_message["content"]))
                output += str(assistant_message["content"]) + "\n"
            if "tool_calls" in assistant_message and assistant_message["tool_calls"]:
                print("3")
                # Iterate through tool_calls to find add_numbers function call
                for tool_call in assistant_message["tool_calls"]:
                    print("4")
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
                    elif tool_call["type"] == "function" and tool_call["function"]["name"] == "go_somewhere":
                        # Extract and print the result
                        print("5")
                        arguments = json.loads(tool_call["function"]["arguments"])
                        print("6")
                        result = go_somewhere(quote(arguments["place_name"]))
                        print(result)
                        print("7")
                        isMap = True

                        tool_response = {
                            "role": "tool",
                            "name": "go_somewhere",
                            "content": f"The coordinates found are longitude: {result['lng']}, latitude: {result['lat']}, at {result['name']}",
                            "tool_call_id": tool_call["id"],
                        }
                        messages.append(tool_response)
                        print(f"AI: {result}")
                        print()
                        output += tool_response["content"]+"\n"

                        data_to_return = {'lng': result['lng'], 'lat': result['lat'], 'name': result['name']}
                        
                    
        except Exception as e:
                print(f"An error occurred: {e}")
        history.append((prompt, output))
    print({'history': (prompt, output)})
    print(jsonify(history))
    return jsonify({'history': (prompt, output)})

if __name__ == '__main__':
    app.run(debug=True)