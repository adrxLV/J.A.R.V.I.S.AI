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
    search_on_wikipedia, search_on_google
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
        # FRIENDLY, CASUAL, HELPFUL PROMPT
        self.prompt_template = (
            f"{self.history_text}\n"
            f"You are {self.botname}, an AI assistant who is also a friendly sidekick for {self.username}. "
            "Be warm, casual, and supportive—like a buddy who always has their back. "
            "Your tone should be fun, easygoing, and helpful, not too formal or robotic. "
            "Keep your answers short (1-2 sentences), unless more detail is needed. Don't be afraid to add a little personality, a joke, or a friendly comment now and then.\n"
            "{ongoing}\nUser: {question}\nAI:"
        )

    def listen(self):
        if self.is_processing:
            return None
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
            except sr.UnknownValueError:
                print("Didn't understand audio")
                self.tts.speak("Sorry, I couldn't catch that. Mind saying it again?")
            except Exception as e:
                print(f"Recognition error: {e}")
        return None

    def chat(self, question):
        """Stream reply and speak by sentence or chunk."""
        self.is_processing = True
        print(f"\n{self.botname}: ", end="", flush=True)
        ongoing = "\n".join(self.history[-6:])

        # Google context addition
        google_context = ""
        if question.lower().startswith("google ") or question.lower().startswith("search on google"):
            google_query = question.partition(" ")[2] if question.lower().startswith("google ") else question.partition("search on google")[2].strip()
            self.speak("Give me a sec, googling that for you...")
            google_results = search_on_google(google_query)
            google_context = f"\n[Google info about '{google_query}']:\n{google_results}\n"

        prompt = self.prompt_template.format(
            ongoing=ongoing + google_context,
            question=question
        )

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
            report = f"It's {temperature}°C in {city} and feels like {feels_like}. {weather.capitalize()} vibes today!"
            self.speak(report)
        except Exception as e:
            self.speak("Oops, couldn't get the weather right now. Blame the clouds!")
            print(f"Weather error: {e}")
        finally:
            self.is_processing = False

    def greet(self):
        hour = datetime.now().hour
        if 6 <= hour < 12:
            greeting = f"Morning, {self.username}! ☀️"
        elif 12 <= hour < 16:
            greeting = f"Hey, good afternoon {self.username}!"
        elif 16 <= hour < 19:
            greeting = f"Evening {self.username}! Hope your day's going awesome."
        else:
            greeting = f"Hey night owl {self.username}!"
        self.speak(greeting)
        time.sleep(1)
        self.speak(f"I'm {self.botname}, your trusty sidekick. What are we up to today?")

    def summarize_and_save_history(self):
        """Summarize conversation and save to file."""
        if not self.history:
            return
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        summary_prompt = (
            "Summarize the following chat in a chill, friendly way (3-5 lines), and start with the date/time (YYYY-MM-DD HH:MM):\n"
            f"Date: {date_str}\n"
            + "\n".join(self.history[-12:])
        )
        summary = ""
        for token in self.ollama.generate_stream(summary_prompt):
            summary += token
        summary_with_date = f"{date_str} - {summary.strip()}"
        append_history(summary_with_date)
        print(f"\n[History saved]\n{summary_with_date}\n")

    def handle_command(self, query):
        """Handle non-chat commands. Return True if handled, else False."""
        commands = {
            'open notepad': (open_notepad, "On it! Notepad coming right up."),
            'open discord': (open_discord, "Firing up Discord for you."),
            'open command prompt': (open_cmd, "Opening command prompt, let's get nerdy!"),
            'open cmd': (open_cmd, "Opening command prompt, let's get nerdy!"),
            'open camera': (open_camera, "Cheese! Turning on the camera."),
            'open calculator': (open_calculator, "Math time! Calculator's open."),
            'ip address': (lambda: self.speak(f'Your IP Address is {find_my_ip()} (don\'t worry, I won\'t leak it!)'), None),
            'weather': (self.weather_report, None),
            'joke': (lambda: self.speak(get_random_joke()), None),
            'news': (self.report_news, None),
            'screenshot': (take_screenshot, "Screenshot time! Hold still..."),
        }

        for key, (func, announce) in commands.items():
            if key in query:
                if announce:
                    self.speak(announce)
                try:
                    func()
                except Exception as e:
                    self.speak(f"Couldn't run that command: {key}. My bad!")
                    print(f"Command error ({key}): {e}")
                return True

        if 'wikipedia' in query:
            self.speak('What should I look up on Wikipedia, friend?')
            self.wait_for_speech_completion()
            search_query = self.listen()
            if search_query:
                try:
                    results = search_on_wikipedia(search_query)
                    short_result = results[:200] + "..." if len(results) > 200 else results
                    self.speak(f"Wikipedia says: {short_result}")
                except Exception as e:
                    self.speak("Wikipedia's not playing nice right now.")
            return True

        if 'youtube' in query:
            self.speak('What do you want to jam to on YouTube?')
            self.wait_for_speech_completion()
            video = self.listen()
            if video:
                self.speak(f"Playing {video} on YouTube—enjoy!")
                play_on_youtube(video)
            return True

        if 'bye' in query or 'goodbye' in query:
            self.speak(f'See ya, {self.username}! Ping me anytime!')
            self.summarize_and_save_history()
            time.sleep(2)
            exit(0)

        return False

    def report_news(self):
        try:
            self.speak("Let me grab some news headlines for you...")
            news = get_latest_news()
            if news:
                self.speak(f"Here's one: {news[0]}")
        except Exception as e:
            self.speak("Couldn't fetch news. I blame the internet goblins!")

    def run(self):
        print(f"Starting {self.botname}...")
        self.greet()
        while True:
            try:
                self.wait_for_speech_completion()
                query = self.listen()
                if not query:
                    continue
                if not self.handle_command(query):
                    self.chat(query)
            except KeyboardInterrupt:
                self.speak("Alright, catch you later!")
                self.summarize_and_save_history()
                break
            except Exception as e:
                print(f"Error: {e}")
                self.speak("Yikes, something went wrong. Want to try again?")

if __name__ == '__main__':
    model = "mistral"  # Or "llama3", etc.
    botname = config('BOTNAME')
    history_text = load_history()
    assistant = PersonalizedAssistant(model, botname, history_text)
    assistant.run()