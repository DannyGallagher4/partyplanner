import openai

openai.api_key = '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'

def parse_request(uinput):
    # Extracting the user input
    user_message = uinput
    query_list = ()
    # Making the OpenAI API call
    try:
        completion = openai.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "split the input into different queries/questions. DO NOT ALTER ANY OF THE WORDS. JUST SEPERATE THEM BASED ON WHETHER THEY ARE DIFFERRENT QUERIES. Seperate the list of queries by a '[qsplit]' in between each query."},
                {"role": "user", "content": user_message}
            ]
        )
        print(completion)
        strlist = completion.choices[0].message.content
        query_list = [q.strip() for q in strlist.split("[qsplit]")]
        print(query_list)
    except Exception as e:
        print("Error", f"An error occurred: {e}")
    return(query_list)