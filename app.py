from flask import Flask, render_template, request
import openai
import requests

app = Flask(__name__)

# Your OpenAI API key
api_key = "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"

openai.api_key = api_key

history = []  # This will store tuples of (prompt, response)



@app.route('/', methods=['GET', 'POST'])
def index():
    
    response_message = None

    if request.method == 'POST':
        prompt = request.form['prompt']

        # Generate OpenAI response
        try:
            completion = openai.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "you are a mathematician"},
                    {"role": "user", "content": prompt}
                ]
            )

            # Get the response message
            response_message = completion.choices[0].message.content

            print(response_message)

            history.append((prompt, response_message))

        except Exception as e:
            print(f"An error occurred: {e}")
            response_message = "An error occurred while processing your request."
        
    return render_template('index.html', response_message=response_message, history=history)

if __name__ == '__main__':
    app.run(debug=True)
    

