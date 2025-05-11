import threading
import io
import queue
import pygame
import requests
import speech_recognition as sr
from langchain_core.prompts import ChatPromptTemplate

from gui import *
from gtts import gTTS
from decouple import config
from datetime import datetime
from functions.online_ops import (
    find_my_ip, get_latest_news, get_random_advice, get_random_joke,
    get_trending_movies, get_weather_report, play_on_youtube,
    search_on_google, search_on_wikipedia, send_email, send_whatsapp_message
)
from functions.os_ops import (
    open_calculator, open_camera, open_cmd, open_notepad,
    open_discord, take_screenshot
)
from langchain_ollama.llms import OllamaLLM

# Configuration settings
USERNAME = config('USER')
BOTNAME = config('BOTNAME')
task_queue = queue.Queue()  # Queue to manage tasks
llm = OllamaLLM(model="mistral")
prompt_conversation = ChatPromptTemplate.from_messages([
    ("system", "You are an AI assistant. Act like Jarvis."),  # edit the pre-prompt if needed
        ("user", "{question}")
])


def speak(text, lang="en"):
    """Convert text to speech and play it."""
    tts = gTTS(text=text, lang=lang)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_fp, "mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass


def listen():
    """Recognize user speech input."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        recognizer.pause_threshold = 2
        audio = recognizer.listen(source)
    try:
        print('Recognizing...')
        query = recognizer.recognize_google(audio, language='en-in')
        return query.lower()
    except Exception:
        speak("Sorry, I couldn't get that.")
        return 'None'


def chat_with_ai(question):
    """Use the AI model to respond to a question."""
    try:
        response = llm.invoke(prompt_conversation.format(question=question))
        return response.strip()
    except Exception as e:
        print(f"Error with AI chat: {e}")
        return "I'm having trouble connecting to the AI model right now."


def handle_command(query):
    """Process voice or text commands."""
    if 'open notepad' in query:
        open_notepad()
    elif 'hello there' in query:
        speak("Hello there!")
        update_ui_output("Hello there!")
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
        update_ui_output(f'Your IP Address is {ip_address}')
    elif 'wikipedia' in query:
        # Handles Wikipedia search requests
        speak('What do you want to search on Wikipedia?')
        search_query = listen()
        results = search_on_wikipedia(search_query)
        speak(f"According to Wikipedia, {results}")
        update_ui_output(results)
    elif 'youtube' in query:
        # Handles YouTube video playback
        speak('What do you want to play on YouTube?')
        video = listen()
        play_on_youtube(video)
    elif 'search on google' in query:
        # Handles Google search requests
        speak('What do you want to search on Google?')
        search_query = listen()
        search_on_google(search_query)
    elif "send a message" in query:
        # Handles sending WhatsApp messages
        speak('Enter the number in the console:')
        number = input("Enter the number: ")
        speak("What is the message?")
        message = listen()
        send_whatsapp_message(number, message)
        speak("Message sent.")
    elif "send an email" in query:
        # Handles sending emails
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
        # Tells a random joke
        joke = get_random_joke()
        speak(joke)
        update_ui_output(joke)
    elif "advice" in query:
        # Provides random advice
        advice = get_random_advice()
        speak(advice)
        update_ui_output(advice)
    elif "trending movies" in query:
        # Fetches trending movies
        task_queue.put(lambda: process_trending_movies())
    elif 'news' in query:
        # Fetches the latest news
        task_queue.put(lambda: process_latest_news())
    elif 'weather' in query:
        # Provides a weather report
        task_queue.put(lambda: give_weather_report())
    elif 'screenshot' in query:
        # Takes a screenshot
        speak("Opening the screenshot software.")
        take_screenshot()
    elif 'question' in query:
        # Handles interacting with the AI assistant
        speak("Would you like to proceed with Text or Speech Mode?")
        mode = listen()
        if 'text' in mode:
            user_input = input("Enter your question: ")
            task_queue.put(lambda: process_text_input(user_input))
        else:
            speak("Proceeding to Speech Mode.")
            question_to_ai = listen()
            task_queue.put(lambda: process_text_input(question_to_ai))


def process_trending_movies():
    """Fetches and displays trending movies."""
    movies = get_trending_movies()
    message = f"Some trending movies are: {', '.join(movies)}"
    speak(message)
    update_ui_output(message)


def process_latest_news():
    """Fetches and displays the latest news."""
    news = get_latest_news()
    speak("Here are the latest news headlines.")
    update_ui_output("\n".join(news))


def give_weather_report():
    """Provides a weather report based on the user's location."""
    ip_address = find_my_ip()
    city = requests.get(f"https://ipapi.co/{ip_address}/city/").text
    weather, temperature, feels_like = get_weather_report(city)
    msg = f"The current temperature is {temperature} degrees, but it feels like {feels_like} degrees. The weather report states: {weather}"
    speak(msg)
    update_ui_output(msg)


def handle_text_input(user_input):
    """Processes text input from the GUI."""
    if user_input.strip():
        formatted_input = f'User: "{user_input}"'
        update_ui_output(formatted_input)  # Display user input in the chat history
        task_queue.put(lambda: process_text_input(user_input))


def process_text_input(user_input):
    """Processes text input and interacts with the AI assistant."""
    if user_input.strip():
        response = chat_with_ai(user_input)
        formatted_response = f"{BOTNAME}: {response}"  # Formats the bot's response
        speak(response)
        update_ui_output(formatted_response)  # Display the response in the chat history


def process_queue():
    """Processes tasks in the queue and executes them in separate threads."""
    while not task_queue.empty():
        task = task_queue.get()
        threading.Thread(target=task).start()
    gui.root.after(100, process_queue)


def start_listening():
    """Starts speech recognition for voice commands."""
    threading.Thread(target=lambda: handle_command(listen())).start()


def greet_user():
    """Greets the user based on the time of day."""
    hour = datetime.now().hour
    if 6 < hour < 12:
        greet = f"Good morning, {USERNAME}!"
    elif 12 <= hour < 16:
        greet = f"Good afternoon, {USERNAME}!"
    elif 16 <= hour < 19:
        greet = f"Good evening, {USERNAME}!"
    else:
        greet = f"Good night, {USERNAME}!"
    speak(greet)
    speak(f"I am {BOTNAME}. How may I assist you?")
    update_ui_output(greet)


if __name__ == '__main__':
    greet_user()  # Greet the user upon starting
    gui.listen_button.configure(command=start_listening)  # Connect the speech button
    gui.submit_button.configure(command=lambda: handle_text_input(gui.input_entry.get()))  # Connect the text input button
    gui.root.after(100, process_queue)  # Start the task queue processing
    gui.run()
