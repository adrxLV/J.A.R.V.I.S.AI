<h1 align="center">🤖 <b>J.A.R.V.I.S.</b> Virtual Assistant</h1>
<p align="center">
  A powerful <b>AI-driven virtual assistant</b> inspired by <b>J.A.R.V.I.S.</b>, capable of controlling your PC and responding intelligently using <b>Ollama models</b>.
</p>

---

## 🚀 About the Project
This Ollama Virtual Assistant is an AI-powered voice assistant that interacts with users through speech recognition and synthesis. Built using Python, it leverages Ollama models to process commands and perform various actions on your computer, making it an intelligent and hands-free assistant.

### 🔥 Features
- 🗣️ **Voice-controlled assistant** – Uses speech recognition to process commands.
- 🤖 **AI-powered responses** – Utilizes Ollama models for intelligent interaction.
- 💻 **PC control capabilities** – Automates tasks and executes system commands.
- 🎙️ **Text-to-Speech (TTS) and Speech Recognition (SR)** – Provides a seamless conversational experience.

---

## 🛠️ Tech Stack
<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Speech%20Recognition-FF9900?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Text--to--Speech-007ACC?style=for-the-badge&logo=azure-speech-services&logoColor=white" />
</p>

---

## 🏗️ Installation & Setup
To run this assistant, follow the steps below:

### 1️⃣ Install Ollama
Download and install Ollama by following the instructions for your OS:

- **Windows:** Download the installer from [Ollama's official website](https://ollama.ai/) and follow the setup process.
- **Mac:** Run the following command:
  ```bash
  brew install ollama
  ```
- **Linux:** Run the following command:
  ```bash
  curl -fsSL https://ollama.ai/install.sh | sh
  ```

### 2️⃣ Install the Mistral Model
Once Ollama is installed, download the **Mistral** model by running on the command line:
```bash
ollama pull mistral
```

### 3️⃣ Create a Virtual Environment
```bash
python -m venv ollama_assistant_env
```

### 4️⃣ Activate the Virtual Environment
- **Windows:**
  ```bash
  ollama_assistant_env\Scripts\activate
  ```
- **Mac/Linux:**
  ```bash
  source ollama_assistant_env/bin/activate
  ```

### 5️⃣ Install Required Dependencies
```bash
pip install pyttsx3 requests speech_recognition python-decouple datetime random pprint langchain_core langchain_ollama langchain
```

### 6️⃣ Configure Environment Variables
Before running the assistant, you need to create a **.env** file in the project root directory with the following structure:
```
USER=YourName
BOTNAME=JARVIS
EMAIL=your.email@example.com
PASSWORD=YourSecurePassword123
NEWS_API_KEY=your_news_api_key
OPENWEATHER_APP_ID=your_openweather_api_key
TMDB_API_KEY=your_tmdb_api_key
```

---

## 🚀 Usage
After installing, simply run the following command to start your AI assistant:
```bash
python main.py
```
Then, speak a command, and the assistant will process it using AI models and execute the corresponding action.

---

## 🎯 Future Improvements
- 🌍 Multi-language support
- 🔍 Enhanced AI reasoning and automation

---

## 📬 Contact
Feel free to reach out for collaboration or suggestions:
- **LinkedIn**: [Adriano Vilhena](https://www.linkedin.com/in/adriano-vilhena-a0493b332/)

---

*This project is under **MIT License***

