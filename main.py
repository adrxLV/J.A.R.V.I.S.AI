import threading
import io
import queue
import pygame
import requests
import speech_recognition as sr
from langchain_core.prompts import ChatPromptTemplate

from gui import gui, update_ui_output
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

# Configurações
USERNAME = config('USER')
BOTNAME = config('BOTNAME')
task_queue = queue.Queue()  # Fila para gerenciar tarefas
llm = OllamaLLM(model="mistral")
prompt_conversation = ChatPromptTemplate.from_messages([
    ("system", "You are an AI assistant. Act like Jarvis."),  # edit the pre-prompt if needed
        ("user", "{question}")
])

def speak(text, lang="en"):
    """Converte texto em fala e reproduz."""
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
    """Reconhece entrada de fala do usuário."""
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
    """Utiliza o modelo de IA para responder uma pergunta."""
    try:
        # Passando question como string diretamente
        response = llm.invoke(prompt_conversation.format(question=question))
        return response.strip()
    except Exception as e:
        print(f"Error with AI chat: {e}")
        return "I'm having trouble connecting to the AI model right now."


def handle_command(query):
    """Processa comandos de voz ou texto."""
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
        speak('What do you want to search on Wikipedia?')
        search_query = listen()
        results = search_on_wikipedia(search_query)
        speak(f"According to Wikipedia, {results}")
        update_ui_output(results)
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
        update_ui_output(joke)
    elif "advice" in query:
        advice = get_random_advice()
        speak(advice)
        update_ui_output(advice)
    elif "trending movies" in query:
        task_queue.put(lambda: process_trending_movies())
    elif 'news' in query:
        task_queue.put(lambda: process_latest_news())
    elif 'weather' in query:
        task_queue.put(lambda: give_weather_report())
    elif 'screenshot' in query:
        speak("Opening the screenshot software.")
        take_screenshot()
    elif 'question' in query:
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
    """Processa e exibe filmes em alta."""
    movies = get_trending_movies()
    message = f"Some trending movies are: {', '.join(movies)}"
    speak(message)
    update_ui_output(message)


def process_latest_news():
    """Processa e exibe as últimas notícias."""
    news = get_latest_news()
    speak("Here are the latest news headlines.")
    update_ui_output("\n".join(news))


def give_weather_report():
    """Fornece um relatório meteorológico."""
    ip_address = find_my_ip()
    city = requests.get(f"https://ipapi.co/{ip_address}/city/").text
    weather, temperature, feels_like = get_weather_report(city)
    msg = f"The current temperature is {temperature} degrees, but it feels like {feels_like} degrees. The weather report states: {weather}"
    speak(msg)
    update_ui_output(msg)


def handle_text_input(user_input):
    """Processa texto inserido na GUI."""
    if user_input.strip():
        formatted_input = f'User: "{user_input}"'
        update_ui_output(formatted_input)  # Exibe o input do usuário no histórico
        task_queue.put(lambda: process_text_input(user_input))

def process_text_input(user_input):
    """Processa a entrada de texto."""
    if user_input.strip():
        response = chat_with_ai(user_input)
        formatted_response = f"{BOTNAME}: {response}"  # Formata a resposta do bot
        speak(response)
        update_ui_output(formatted_response)  # Exibe a resposta no histórico

def process_queue():
    """Processa a fila de tarefas."""
    while not task_queue.empty():
        task = task_queue.get()
        threading.Thread(target=task).start()
    gui.root.after(100, process_queue)


def start_listening():
    """Inicia o reconhecimento de fala."""
    threading.Thread(target=lambda: handle_command(listen())).start()


def greet_user():
    """Cumprimenta o usuário ao iniciar."""
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
    greet_user()  # Cumprimenta o usuário ao iniciar
    gui.listen_button.config(command=start_listening)  # Conecta o botão de fala
    gui.submit_button.config(command=lambda: handle_text_input(gui.input_entry.get()))  # Conecta o botão de texto
    gui.root.after(100, process_queue)  # Inicia o processamento da fila
    gui.run()
