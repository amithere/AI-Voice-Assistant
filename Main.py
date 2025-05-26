from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealTimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import os
import threading
import json

env_vars = dotenv_values(".env")
Username = env_vars.get("USERNAME")
AssistantName = env_vars.get("ASSISTANT_NAME")
DefaultMessage = f'''{Username} : Hello {AssistantName}, how are you?
{AssistantName} : Hello {Username}, I am doing well, thank you! How can I assist you today?'''
subprocesses = []
Functions = ["open", "close", "youtube search", "google search", "play", "pause", "stop", "next", "previous", "volume_up", "volume_down"]

def ShowDefaultChatIfNoChat():
    File = open(r'Data/ChatLog.json', 'r', encoding='utf-8')
    if len(File.read()) < 5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f:
            f.write("")

        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as f:
            f.write(DefaultMessage)
        
def ReadChatLogJson():
    with open(r'Data/ChatLog.json', 'r', encoding='utf-8') as f:
        try:
            chatlog_data = json.load(f)
            return chatlog_data
        except json.JSONDecodeError:
            return []
        
def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry['role'] == 'user':
            formatted_chatlog += f"{Username} : {entry['content']}\n"
        elif entry['role'] == 'assistant':
            formatted_chatlog += f"{AssistantName} : {entry['content']}\n"
        
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f:
        f.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnUI():
    File = open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8')
    chatlog = File.read()
    if len(str(chatlog))>0:
        lines = chatlog.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8')
        File.write(result)
        File.close()

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChat()
    ChatLogIntegration()
    ShowChatsOnUI()

InitialExecution()

def MainExecution():

    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Processing...")
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"Decision: {Decision}")
    print("")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])
    
    Merged_Query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if TaskExecution is False:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True
    
    if ImageExecution is True:
        with open(r"Frontend/Files/ImageGeneration.data", 'w', encoding='utf-8') as f:
            f.write(f"{ImageGenerationQuery}")
        try:
            p1 = subprocess.Popen(['python', r'Backend/ImageGeneration.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE, shell=False)
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error starting Image Generation: {e}")
    
    if G and R or R:
        SetAssistantStatus("Searching...")
        Answer = RealTimeSearchEngine(QueryModifier(Merged_Query))
        ShowTextToScreen(f"{AssistantName} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Processing...")
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{AssistantName} : {Answer}")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealTimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{AssistantName} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "Goodbye..."
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{AssistantName} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering...")
                os._exit(1)

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()

            if "Available..." in AIStatus:
                sleep(0.5)
            else:
                SetAssistantStatus("Available...")

def SecondThread():
    GraphicalUserInterface()

if __name__  == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()


