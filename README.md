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
   - Fill in your Discord bot token and Gemini API key

4. **Run the bot**:
   ```bash
   python bot.py
   ```

## Deployment on Discloud

For 24/7 hosting, you can deploy your bot on Discloud:

### Prerequisites for Discloud
1. Create an account at [Discloud](https://discloud.app/)
2. Have your bot files ready (already included in this project)

### Deployment Steps
1. **Prepare your files**:
   - Ensure `discloud.config` is present (already included)
   - Make sure `bot.py` is your main file

2. **Upload to Discloud**:
   - Go to your Discloud dashboard
   - Click "Upload App"
   - Zip all your bot files including:
     - `bot.py`
     - `discloud.config`
     - Any other project files
   - Upload the zip file

3. **Set Environment Variables**:
   - In your Discloud app dashboard, go to "Environment Variables"
   - Add your secrets:
     - `DISCORD_BOT_TOKEN`: Your Discord bot token
     - `GEMINI_API_KEY`: Your Google Gemini API key

4. **Start the bot**:
   - Click "Start" in your Discloud dashboard
   - Your bot will be online 24/7!

### Discloud Configuration
The included `discloud.config` file contains:
- **Type**: Bot application
- **Main File**: bot.py
- **RAM**: 512MB (sufficient for this bot)
- **Version**: Latest Python version

## Bot Usage