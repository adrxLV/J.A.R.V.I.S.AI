# Imports
from time import sleep
import io
import sys
import pygame
import pyttsx3
import openai
import requests
import speech_recognition as sr

from gtts import gTTS
from bs4 import BeautifulSoup
from httpx import Client
from swarm import Swarm, Agent
from decouple import config
from datetime import datetime
from random import choice
from pprint import pprint

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

from functions.online_ops import (
    find_my_ip, get_latest_news, get_random_advice, get_random_joke,
    get_trending_movies, get_weather_report, play_on_youtube,
    search_on_google, search_on_wikipedia, send_email, send_whatsapp_message
)
from functions.os_ops import (
    open_calculator, open_camera, open_cmd, open_notepad,
    open_discord, take_screenshot
)
from utils import opening_text

def give_weather_report():
    ip_address = find_my_ip()
    city = requests.get(f"https://ipapi.co/{ip_address}/city/").text
    weather, temperature, feels_like = get_weather_report(city)
    speak(
        f"The current temperature is {temperature} degrees, but it feels like {feels_like} degrees. The weather report states: {weather}"
    )
    print(f"Description: {weather}\nTemperature: {temperature}\nFeels like: {feels_like}")

def speak(text, lang="en"):
    """Convert text to speech and play it without saving a file."""
    tts = gTTS(text=text, lang=lang)

    # Save to a BytesIO object instead of a file
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    # Initialize pygame mixer and play audio
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_fp, "mp3")
    pygame.mixer.music.play()

    # Keep the program running until the audio finishes
    while pygame.mixer.music.get_busy():
        pass


# Configs
USERNAME = config('USER')
BOTNAME = config('BOTNAME')

engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 190)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[2].id)

# AI to chat
llm = OllamaLLM(model="mistral")  # change the model if needed
prompt_conversation = ChatPromptTemplate.from_messages([
    ("system", "You are an AI assistant. Act like Jarvis."),  # edit the pre-prompt if needed
    ("user", "{question}")
])


def listen():
    """Captures the speech"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        recognizer.pause_threshold = 2
        audio = recognizer.listen(source)

    try:
        print('Recognizing...')
        query = recognizer.recognize_google(audio, language='en-in')
    except Exception:
        speak("Sorry, I couldn't get that.")
        return 'None'
    return query.lower()


def chat_with_ai(question):
    """AI to answer questions"""
    response = llm.invoke(prompt_conversation.format(question=question))
    return response.strip()


def greet_user():
    """Greets user with the date"""
    hour = datetime.now().hour
    if 6 < hour < 12:
        speak(f"Good morning {USERNAME}")
    elif 12 <= hour < 16:
        speak(f"Good afternoon {USERNAME}")
    elif 16 <= hour < 19:
        speak(f"Good evening {USERNAME}")
    elif 19 >= hour < 6:
        speak(f"Good night {USERNAME}")
    speak(f"I am {BOTNAME}. How may I assist you?")


if __name__ == '__main__':
    trigger_speech_mode = "question"
    greet_user()
    while True:
        query = listen()

        if 'open notepad' in query:
            open_notepad()
        elif 'open discord' in query:
            open_discord()
        elif 'open command prompt' in query or 'open cmd' in query:
            open_cmd()
        elif 'open camera' in query:
            open_camera()
        elif 'open calculator' in query:
            open_calculator()
        elif 'ip address' in query:
            ip_address = find_my_ip()
            speak(f'Your IP Address is {ip_address}.')
            print(f'Your IP Address is {ip_address}')
        elif 'wikipedia' in query:
            speak('What do you want to search on Wikipedia?')
            search_query = listen()
            results = search_on_wikipedia(search_query)
            speak(f"According to Wikipedia, {results}")
            print(results)
        elif 'youtube' in query:
            speak('What do you want to play on YouTube?')
            video = listen()
            play_on_youtube(video)
        elif 'search on google' in query:
            speak('What do you want to search on Google?')
            search_query = listen()
            search_on_google(search_query)
        elif "send a message" in query:  # go to online_ops whatsapp function and change the country code
            speak('Enter the number in the console:')
            number = input("Enter the number: ")
            speak("What is the message?")
            message = listen()
            try:
                send_whatsapp_message(number, message)
                speak("Message sent.")
            except:
                print("Error in sending the message")
        elif "send an email" in query:
            speak("Enter email address in the console:")
            receiver_address = input("Enter email address: ")
            speak("What should be the subject?")
            subject = listen().capitalize()
            speak("What is the message?")
            message = listen().capitalize()
            if send_email(receiver_address, subject, message):
                speak("Email sent.")
            else:
                speak("Error sending email.")
        elif 'joke' in query:
            joke = get_random_joke()
            speak(joke)
            print(joke)
        elif "advice" in query:
            advice = get_random_advice()
            speak(advice)
            print(advice)
        elif "trending movies" in query:
            movies = get_trending_movies()
            speak(f"Some trending movies are: {', '.join(movies)}")
            print(*movies, sep='\n')
        elif 'news' in query:
            news = get_latest_news()
            speak("Here are the latest news headlines.")
            print(*news, sep='\n')
        elif 'weather' in query:
            give_weather_report()
        elif 'screenshot' in query:
            speak("Opening the screenshot software.")
            take_screenshot()
        elif trigger_speech_mode in query:
            print(f"{BOTNAME}: Would you like to proceed with Text or Speech Mode?")
            speak("Would you like to proceed with Text or Speech Mode?")
            mode = listen()
            if 'text' in mode:
                response = chat_with_ai(input())
                print(response)
                speak(response)
            else:
                speak("Proceeding to Speech Mode.")
                question_to_ai = listen()
                response = chat_with_ai(question_to_ai)
                print(response)
                speak(response)
        elif 'bye' in query:
            speak(f'Bye bye {USERNAME}, see you later!')
            sleep(3)
            speak('Proceeding to shutdown.')
            speak('System offline.')
            break
