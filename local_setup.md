# Running برعي Bot Locally on Your PC

## Step 1: Download Files from Replit
1. In your Replit project, click the project name at the top
2. Select "Download as zip"
3. Extract the zip file to a folder on your PC (e.g., `C:\BoraBot\`)

## Step 2: Install Python
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Install for all users

## Step 3: Install Required Packages
Open Command Prompt in your bot folder and run:
```cmd
pip install discord.py google-genai
```

## Step 4: Set Up Environment Variables
Create a file called `.env` in your bot folder with:
```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## Step 5: Run the Bot
Double-click `run_bot.bat` or run in Command Prompt:
```cmd
python bot.py
```

## Step 6: Keep Bot Running 24/7
- Keep your PC on
- The bot will run continuously until you close the Command Prompt window
- To restart: Close the window and run again

## Troubleshooting
- If Python not found: Reinstall Python with "Add to PATH" checked
- If packages not found: Run the pip install command again
- If bot doesn't connect: Check your Discord token and Gemini API key

Your bot برعي will now run locally on your PC!