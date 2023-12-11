from flask import Flask, render_template, request
from openai import OpenAI
import requests

app = Flask(__name__)

# Your OpenAI API key
api_key = "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"
client = OpenAI(api_key=api_key)

@app.route('/', methods=['GET', 'POST'])
def index():
    response_message = None

    if request.method == 'POST':
        prompt = request.form['prompt']
        prompt = prompt.replace(" ", "+")

        result = requests.get(f"http://www.omdbapi.com/?apikey=bf7dfc64&t={prompt}&plot=full")

        if result.json()["Response"] == "True":
            title = result.json()["Title"]
            author = result.json()["Writer"]
            genre = result.json()["Genre"]
            plot = result.json()["Plot"]

        # Generate OpenAI response
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a writer of a short story. Write a 2000ish word story that is a sequel to whatever is provided."},
                    {"role": "user", "content": f"In the style of {author}, with genre {genre}, write the short story that would be a plausible follow up to {title}, which had a plot of {plot}. This short story should follow logically from the end of {title} into a new story."}
                ]
            )

            # Get the response message
            response_message = completion.choices[0].message.content

            print(response_message)

    return render_template('testindex.html', response_message=response_message)

if __name__ == '__main__':
    app.run(debug=True)
