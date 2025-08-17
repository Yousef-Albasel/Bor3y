# Discord AI Bot with Gemini

A Discord bot that uses Google's Gemini AI to respond to mentions with intelligent, AI-generated answers.

## Features

- 🤖 AI-powered responses using Google Gemini API
- 💬 Responds when mentioned in Discord channels
- 🔧 Built-in error handling and logging
- 📊 Status monitoring commands
- 🚀 Easy setup and deployment

## Setup Instructions

### Prerequisites

1. **Discord Bot Token**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to "Bot" section and create a bot
   - Copy the bot token
   - Enable "Message Content Intent" in the bot settings

2. **Google Gemini API Key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the API key

### Installation

1. **Clone or download the bot files**

2. **Install required dependencies**:
   ```bash
   pip install discord.py google-genai python-dotenv
   ```

3. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Fill in your Discord bot token and Gemini API key:
   