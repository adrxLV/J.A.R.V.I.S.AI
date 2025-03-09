#imports
import pyttsx3
import requests
import speech_recognition as sr
from decouple import config
from datetime import datetime
from random import choice
from pprint import pprint

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from functions.online_ops import find_my_ip, get_latest_news, get_random_advice, get_random_joke, get_trending_movies, \
    get_weather_report, play_on_youtube, search_on_google, search_on_wikipedia, send_email, send_whatsapp_message
from functions.os_ops import open_calculator, open_camera, open_cmd, open_notepad, open_discord
from utils import opening_text

# configs
USERNAME = config('USER')
BOTNAME = config('BOTNAME')

engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 190)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# AI to chat
llm = OllamaLLM(model="mistral")  # change the model if needed
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI assistant. Act like Jarvis."), #edit the pre-prompt if needed
    ("user", "{question}")
])


def speak(text: str):
    """speaks the given text"""
    engine.say(text)
    engine.runAndWait()


def listen():
    """captures the speach"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)

    try:
        print('Recognizing...')
        query = recognizer.recognize_google(audio, language='en-in')
    except Exception:
        speak('Sorry, I could not understand. Could you please say that again?')
        return 'None'
    return query.lower()


def chat_with_ai(question):
    """AI to awenser questions"""
    response = llm.invoke(prompt.format(question=question))
    return response.strip()


def greet_user():
    """greets user with the date"""
    hour = datetime.now().hour
    if 6 < hour < 12:
        speak(f"Good Morning {USERNAME}")
    elif 12 <= hour < 16:
        speak(f"Good afternoon {USERNAME}")
    elif 16 <= hour < 19:
        speak(f"Good Evening {USERNAME}")
    elif 19 >= hour < 6:
        speak(f"Good night {USERNAME}")
    speak(f"I am {BOTNAME}. How may I assist you?")


if __name__ == '__main__':
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
        elif "send a message" in query:
            speak('Enter the number in the console:')
            number = input("Enter the number: ")
            speak("What is the message?")
            message = listen()
            send_whatsapp_message(number, message)
            speak("Message sent.")
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
            ip_address = find_my_ip()
            city = requests.get(f"https://ipapi.co/{ip_address}/city/").text
            weather, temperature, feels_like = get_weather_report(city)
            speak(f"The current temperature is {temperature}, but it feels like {feels_like}. The weather report states: {weather}")
            print(f"Description: {weather}\nTemperature: {temperature}\nFeels like: {feels_like}")
        elif 'jarvis' in query:
            response = chat_with_ai(query)
            speak(response)
            print(response)
