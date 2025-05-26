from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import asyncio
import os
import platform
import subprocess

is_windows = platform.system() == "Windows"

if is_windows:
    from AppOpener import close, open as appopen
    import keyboard

env_vars = dotenv_values('.env')

Username = env_vars.get('USERNAME')

GroqAPIKey = env_vars.get('GROQ_API_KEY')

classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "ZOLcW", "gsrt_vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
           "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOe",
           "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there is anything else I can help you with.",
    "I am at your service for any additional question or support you may need-don't hesitate to ask."
]

messages = []

SystemChatBot = [
    {"role": "system", "content": f"Hello, I am {Username}, You are a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."},
]

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
    def OpenNotepad(File):
        system_os = platform.system()
        if system_os == 'Windows':
            default_text_editor = 'notepad.exe'
            subprocess.Popen([default_text_editor, File])
        elif system_os == "Darwin":
            subprocess.Popen(["open", "-a", "TextEdit", File])
        elif system_os == "Linux":
            subprocess.Popen(["xdg-open", File])
        else:
            print(f"Unsupported OS: {system_os}")

    def ContentWiterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
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
        return Answer
    Topic: str = Topic.replace("Content ", "")
    ContentByAI = ContentWiterAI(Topic)

    with open(rf"Data/{Topic.lower().replace(' ', '')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)
        file.close()

    OpenNotepad(rf"Data/{Topic.lower().replace(' ', '')}.txt")
    return True

def YoouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def OpenApp(app, sess=requests.session()):
    try:
        if is_windows:
            appopen(app, match_closest=True, output=True, throw_error=True)
            return True
        else:
            subprocess.run(["open", "-a", app])
            return True
    except:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]
        
        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                printf("Failed to retrieve search results")
            return None
        
        html = search_google(app)

        if html:
            link = extract_links(html)[0]
            webopen(link)

        return True
    
def CloseApp(app):

    try:
        if is_windows:
            if "chrome" in app:
                pass
            else:
                close(app, match_closest=True, output=True, throw_error=True)
                return True
        else:
            subprocess.run(["osascript", "-e", f'tell application "{app}" to quit'])
        return True
    except Exception as e:
        print(f"Error closing app: {e}")
        return False
        
def System(command):

    system_os = platform.system()
    def mute():
        if system_os == "Windows":
            keyboard.press_and_release("volume mute")
        else:
            subprocess.run(["osascript", "-e", 'set volume output muted true'])

    def unmute():
        if system_os == "Windows":
            keyboard.press_and_release("volume mute")
        else:
            subprocess.run(["osascript", "-e", 'set volume output muted false'])

    def volume_up():
        if system_os == "Windows":
            keyboard.press_and_release("volume up")
        else:
            subprocess.run(["osascript", "-e", 'set volume output volume ((output volume of (get volume settings)) + 10)'])

    def volume_down():
        if system_os == "Windows":
            keyboard.press_and_release("volume down")
        else:
            subprocess.run(["osascript", "-e", 'set volume output volume ((output volume of (get volume settings)) - 10)'])

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    return True

async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith("open "):
            if "open it " in command:
                pass
            if "open file" == command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("general "):
            pass
        elif command.startswith("realtime "):
            pass
        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)
        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)
        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)
        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YoouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
        else:
            print(f"No function found for {command}")
        
    results = await asyncio.gather(*funcs)

    for result in results:
        if (isinstance(result, str)):
            yield result
        else:
            yield result

    
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True


#Content("application for sick leave")
#GoogleSearch("car")
#PlayYoutube("kk music")
#OpenApp("facebook")
#System("mute")


if __name__ == "__main__":
    # Test the function
    while True:
        asyncio.run(Automation(["open facebook", "open instagram", "open telegram", "play zindaa", "content song for me"]))
    

