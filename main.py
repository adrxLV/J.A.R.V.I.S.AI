import threading
import time
import requests
import pyttsx3
import speech_recognition as sr
from decouple import config
from datetime import datetime
import os

from ollama_streaming import StreamingOllama
from functions.online_ops import (
    find_my_ip, get_latest_news, get_random_joke,
    get_weather_report, play_on_youtube,
    search_on_wikipedia
)
from functions.os_ops import (
    open_calculator, open_camera, open_cmd, open_notepad,
    open_discord, take_screenshot
)

HISTORY_FILE = "ai_conversation_history.txt"

def load_history():
    """Read saved conversation history."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def append_history(summary):
    """Append summary to history file."""
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(summary.strip() + "\n\n")

class Speech:
    """Text-to-speech system."""

    def __init__(self):
        try:
            self.engine = pyttsx3.init('sapi5')
            self.engine.setProperty('rate', 180)
            self.engine.setProperty('volume', 1.0)
            voices = self.engine.getProperty('voices')
            if voices and len(voices) > 1:
                self.engine.setProperty('voice', voices[2].id)
            self.tts_available = True
            print("TTS ready")
        except Exception as e:
            print(f"TTS failed: {e}")
            self.tts_available = False
        self.is_speaking = False
        self.speech_lock = threading.Lock()

    def speak(self, text):
        if not text or not text.strip():
            return
        with self.speech_lock:
            if not self.tts_available:
                print(f"TTS unavailable. Text: {text}")
                return
            try:
                self.is_speaking = True
                print(f"Speaking: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")
            finally:
                self.is_speaking = False

    def is_busy(self):
        return self.is_speaking

class PersonalizedAssistant:
    def __init__(self, model_name, botname, history_text):
        self.username = config('USER')
        self.botname = botname
        self.tts = Speech()
        self.is_processing = False
        self.model = model_name
        self.ollama = StreamingOllama(model=self.model)
        self.history = []
        self.history_text = history_text
        self.prompt_template = (
            f"{self.history_text}\n"
            f"You are an AI assistant named {self.botname}. Give concise, helpful responses in 1-2 sentences.\n"
            "{ongoing}\nUser: {question}\nAI:"
        )

    def listen(self):
        if self.is_processing:
            return 'None'
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        with sr.Microphone() as source:
            print('Listening...')
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
                print('Recognizing...')
                query = recognizer.recognize_google(audio, language='en-in')
                print(f"You said: {query}")
                return query.lower()
            except sr.WaitTimeoutError:
                print("Timeout")
                return 'None'
            except sr.UnknownValueError:
                print("Didn't understand audio")
                self.tts.speak("Sorry, I couldn't understand that.")
                return 'None'
            except Exception as e:
                print(f"Recognition error: {e}")
                return 'None'

    def chat(self, question):
        """Stream reply and speak by sentence or chunk."""
        self.is_processing = True
        print(f"\n{self.botname}: ", end="", flush=True)
        ongoing = "\n".join(self.history[-6:])
        prompt = self.prompt_template.format(ongoing=ongoing, question=question)
        buffer = ""
        sentence_endings = {".", "!", "?"}
        max_chunk = 122

        def speak_chunk(chunk):
            self.tts.speak(chunk)
            while self.tts.is_busy():
                time.sleep(0.07)

        reply = ""
        for token in self.ollama.generate_stream(prompt):
            print(token, end="", flush=True)
            buffer += token
            reply += token
            if (buffer and buffer[-1] in sentence_endings) or len(buffer) > max_chunk:
                chunk = buffer.strip()
                if chunk:
                    speak_chunk(chunk)
                buffer = ""

        if buffer.strip():
            speak_chunk(buffer.strip())

        self.history.append(f"User: {question}")
        self.history.append(f"AI: {reply.strip()}")
        self.is_processing = False

    def speak(self, text):
        print(f"{self.botname}: {text}")
        self.tts.speak(text)

    def wait_for_speech_completion(self):
        while self.tts.is_busy():
            time.sleep(0.1)

    def weather_report(self):
        try:
            self.is_processing = True
            ip_address = find_my_ip()
            city = requests.get(f"https://ipapi.co/{ip_address}/city/", timeout=5).text
            weather, temperature, feels_like = get_weather_report(city)
            report = f"The temperature is {temperature} degrees, feels like {feels_like}. Weather: {weather}"
            self.speak(report)
        except Exception as e:
            self.speak("Sorry, I couldn't get the weather report.")
            print(f"Weather error: {e}")
        finally:
            self.is_processing = False

    def greet(self):
        hour = datetime.now().hour
        if 6 <= hour < 12:
            greeting = f"Good morning {self.username}"
        elif 12 <= hour < 16:
            greeting = f"Good afternoon {self.username}"
        elif 16 <= hour < 19:
            greeting = f"Good evening {self.username}"
        else:
            greeting = f"Good night {self.username}"
        self.speak(greeting)
        time.sleep(1)
        self.speak(f"I am {self.botname}. How may I assist you?")

    def summarize_and_save_history(self):
        """Summarize conversation and save to file."""
        if not self.history:
            return
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        summary_prompt = (
            "Briefly summarize the conversation below, in Portuguese, in 3-5 lines, "
            "including the date at the beginning of the summary (format YYYY-MM-DD HH:MM):\n"
            f"Date: {date_str}\n"
            + "\n".join(self.history[-12:])
        )
        summary = ""
        for token in self.ollama.generate_stream(summary_prompt):
            summary += token
        summary_with_date = f"{date_str} - {summary.strip()}"
        append_history(summary_with_date)
        print(f"\n[History saved]\n{summary_with_date}\n")

    def run(self):
        print(f"Starting {self.botname}...")
        self.greet()
        while True:
            try:
                self.wait_for_speech_completion()
                query = self.listen()
                if query == 'None' or not query.strip():
                    continue
                if 'open notepad' in query:
                    self.speak("Opening notepad")
                    open_notepad()
                elif 'open discord' in query:
                    self.speak("Opening Discord")
                    open_discord()
                elif 'open command prompt' in query or 'open cmd' in query:
                    self.speak("Opening command prompt")
                    open_cmd()
                elif 'open camera' in query:
                    self.speak("Opening camera")
                    open_camera()
                elif 'open calculator' in query:
                    self.speak("Opening calculator")
                    open_calculator()
                elif 'ip address' in query:
                    try:
                        ip_address = find_my_ip()
                        self.speak(f'Your IP Address is {ip_address}')
                    except Exception as e:
                        self.speak("Could not find IP address")
                elif 'wikipedia' in query:
                    self.speak('What do you want to search on Wikipedia?')
                    self.wait_for_speech_completion()
                    search_query = self.listen()
                    if search_query != 'None':
                        try:
                            results = search_on_wikipedia(search_query)
                            short_result = results[:200] + "..." if len(results) > 200 else results
                            self.speak(f"According to Wikipedia: {short_result}")
                        except Exception as e:
                            self.speak("Could not search Wikipedia")
                elif 'youtube' in query:
                    self.speak('What do you want to play on YouTube?')
                    self.wait_for_speech_completion()
                    video = self.listen()
                    if video != 'None':
                        self.speak(f"Playing {video} on YouTube")
                        play_on_youtube(video)
                elif 'weather' in query:
                    self.weather_report()
                elif 'joke' in query:
                    try:
                        joke = get_random_joke()
                        self.speak(joke)
                    except Exception as e:
                        self.speak("Sorry, I couldn't get a joke right now")
                elif 'news' in query:
                    try:
                        self.speak("Getting latest news")
                        news = get_latest_news()
                        if news:
                            self.speak(f"Here's a headline: {news[0]}")
                    except Exception as e:
                        self.speak("Could not get news")
                elif 'screenshot' in query:
                    self.speak("Taking screenshot")
                    take_screenshot()
                elif 'bye' in query or 'goodbye' in query:
                    self.speak(f'Goodbye {self.username}! See you later!')
                    self.summarize_and_save_history()
                    time.sleep(2)
                    break
                else:
                    self.chat(query)
            except KeyboardInterrupt:
                self.speak("Goodbye!")
                self.summarize_and_save_history()
                break
            except Exception as e:
                print(f"Error: {e}")
                self.speak("I encountered an error. Please try again.")

if __name__ == '__main__':
    model = "mistral"  # Or "llama3", etc.
    botname = config('BOTNAME')
    history_text = load_history()
    assistant = PersonalizedAssistant(model, botname, history_text)
    assistant.run()