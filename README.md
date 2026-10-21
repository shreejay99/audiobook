# 📚 AI-Powered Audiobook Generator & Study Companion

An intelligent, full-stack Python application that converts PDF documents into high-quality audiobooks featuring real-time, karaoke-style word highlighting and integrated AI document analysis.

## ✨ Key Features

* 🎧 **Neural Text-to-Speech:** Uses Microsoft Edge Neural Voices (`edge-tts`) to deliver natural, human-like voice synthesis across multiple regional accents and genders.
* 🎤 **Karaoke-Style Word Highlighting:** Synchronizes audio playback with WebVTT timestamp tracks, highlighting spoken text in real time via an embedded HTML5 player.
* 🤖 **Gemini 1.5 Flash AI Integration:** Powered by Google Gemini and LangChain to automatically generate concise chapter/document summaries and answer natural language questions about the uploaded content.
* 📜 **Persistent Session History:** Uses an embedded SQLite database to save generated audio files, text summaries, and voice settings so you can resume listening anytime.
* 🚀 **Streamlit Web UI:** Clean, dual-tab dashboard for document upload, live audio generation, document Q&A, and audiobook library management.

## 🛠️ Tech Stack

* **Frontend:** Streamlit, HTML5, WebVTT API
* **LLM & Orchestration:** Google Gemini Pro (`gemini-1.5-flash`), LangChain
* **TTS Engine:** Edge-TTS (`edge-tts`)
* **Document Parsing:** PyPDF
* **Database & Persistence:** SQLite3