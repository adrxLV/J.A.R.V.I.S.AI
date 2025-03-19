<p align="center">
  <img src="https://mir-s3-cdn-cf.behance.net/project_modules/disp/0f3ed952323519.5608d8fce47b2.png" width="200" height="200" />
</p>

<h1 align="center">🤖 <b>J.A.R.V.I.S.</b> Virtual Assistant</h1>
<p align="center">
  A powerful <b>AI-driven virtual assistant</b> inspired by <b>J.A.R.V.I.S.</b>, capable of controlling your PC and responding intelligently using <b>Ollama models</b>.
</p>

---

## 🚀 About the Project
This Ollama Virtual Assistant is an AI-powered voice assistant that interacts with users through speech recognition and synthesis. Built using Python, it uses Ollama models to process commands and perform various actions on your computer, making it an intelligent and hands-free assistant.
<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Speech%20Recognition-FF9900?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Text--to--Speech-007ACC?style=for-the-badge&logo=azure-speech-services&logoColor=white" />
</p>

### 🔥 Features
- 🗣️ **Voice-controlled assistant** – Uses speech recognition to process commands.
- 🤖 **AI-powered responses** – Utilizes Ollama models for intelligent interaction.
- 💻 **PC control capabilities** – Automates tasks and executes system commands.
- 🎙️ **Text-to-Speech (TTS) and Speech Recognition (SR)** – Provides a seamless conversational experience.

---


## **Table of Contents**

- [🚀 About the Project](#-about-the-project)  
- [🏗️ Installation & Setup](#%EF%B8%8F-installation--setup)  
- [🚀 Usage](#-usage)  
- [📜Project Structure](#-project-structure)  
- [License](#license)  

## 🏗️ Installation & Setup
To run this assistant, follow the steps below:

### Clone this Repo
```
git clone https://github.com/adrxLV/J.A.R.V.I.S.AI.git
cd J.A.R.V.I.S.AI
```

### Install Ollama
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

### Install the Mistral Model
Once Ollama is installed, download the **Mistral** model by running on the command line:
```bash
ollama pull mistral
```

### Create a Virtual Environment
```bash
python -m venv ollama_assistant_env
```

### Activate the Virtual Environment
- **Windows:**
  ```bash
  ollama_assistant_env\Scripts\activate
  ```
- **Mac/Linux:**
  ```bash
  source ollama_assistant_env/bin/activate
  ```

### Install Required Dependencies
```bash
pip install pyttsx3 requests SpeechRecognition python-decouple langchain_core langchain_ollama langchain
```

### Configure Environment Variables
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

## 📜 Project Structure
```
├── J.A.R.V.I.S.AI/
│   ├──functions/                 # some functions to make the V.A. work;
│   │   ├── online_ops.py         # Online services and operations;
│   │   ├── os_ops.py             # Local operations;
│   ├── main.py                   # Main entry point;
│   ├── utils.py                  # Some utility info;
│   ├── .env                      # Api keys storage, e-mail, username, bot name, etc.
├──
```
---

<table align="center">
  <tr>
    <td align="center">
      <a href="https://ollama.com/">
        <img src="https://dev-to-uploads.s3.amazonaws.com/uploads/articles/qbosw7lyg8enfdqqi8ox.png" alt="Ollama" style="width: 200px; height: 200px;">
      </a>
    </td>
    <td align="center">
      <a href="https://mistral.ai">
        <img src="https://framerusercontent.com/images/DLqZSWwUcLevgxcdron1gb0WZ7c.png" alt="Mistral" style="width: 200px; height: 200px;">
      </a>
    </td>
  </tr>
</table>



---
## License
*This project is licensed under the **MIT License** - see the LICENSE file for details.*

