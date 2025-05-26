from groq import Groq
from json import dump, load
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("USERNAME")
AssistantName = env_vars.get("ASSISTANT_NAME")
GroqAPIKey = env_vars.get("GROQ_API_KEY")

groq_client = Groq(api_key = GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {AssistantName} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System},
]

try:
    with open("Data/ChatLog.json", "r") as file:
        messages = load(file)
except FileNotFoundError:
    with open(r"Data/ChatLog.json", "w") as file:
        dump([], file)


def RealTimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed, \n"
    data += f"Day: {day} \n Date:{date} \n Month: {month} \n Year: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds \n"
    return data

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

def ChatBot(Query):
    """This function sends the user's query to the chatbot and return the AI's response."""

    try:
        with open("Data/ChatLog.json", "r") as file:
            messages = load(file)
        
        messages.append({"role": "user", "content": f"{Query}"})

        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealTimeInformation()}] + messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")

        messages.append({"role": "assistant", "content": Answer})

        with open("Data/ChatLog.json", "w") as file:
            dump(messages, file, indent=4)

        return AnswerModifier(Answer)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        with open(r"Data/ChatLog.json", "w") as file:
            dump([], file)
        return ChatBot(Query)
    
if __name__ == "__main__":
    # Test the function
    while True:
        user_input = input("Enter your Question: ")
        print(ChatBot(user_input))
        