import os
import logging
import asyncio
import discord
from discord.ext import commands
from google import genai
from google.genai import types

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Gemini client
try:
    gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    logger.info("Gemini client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    gemini_client = None

class GeminiBot(commands.Bot):
    def __init__(self):
        # Set up bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="mentions for AI assistance"
        )
        await self.change_presence(activity=activity)
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore messages from the bot itself
        if message.author == self.user:
            return
        
        # Check if the bot is mentioned
        if self.user in message.mentions:
            await self.handle_mention(message)
        
        # Process commands
        await self.process_commands(message)
    
    async def handle_mention(self, message):
        """Handle when the bot is mentioned"""
        try:
            # Show typing indicator
            async with message.channel.typing():
                # Extract the question/content (remove the mention)
                content = message.content
                for mention in message.mentions:
                    content = content.replace(f'<@{mention.id}>', '').strip()
                    content = content.replace(f'<@!{mention.id}>', '').strip()
                
                if not content:
                    await message.reply("Hi! Please ask me a question and I'll help you with an AI-generated response!")
                    return
                
                logger.info(f"Processing question from {message.author}: {content}")
                
                # Get AI response
                ai_response = await self.get_gemini_response(content)
                
                if ai_response:
                    # Split long responses if needed (Discord has 2000 character limit)
                    if len(ai_response) > 2000:
                        chunks = [ai_response[i:i+2000] for i in range(0, len(ai_response), 2000)]
                        for i, chunk in enumerate(chunks):
                            if i == 0:
                                await message.reply(chunk)
                            else:
                                await message.channel.send(chunk)
                    else:
                        await message.reply(ai_response)
                else:
                    await message.reply("Sorry, I couldn't generate a response right now. Please try again later.")
                
        except discord.HTTPException as e:
            logger.error(f"Discord API error: {e}")
            await message.reply("Sorry, there was an error sending my response. Please try again.")
        except Exception as e:
            logger.error(f"Unexpected error handling mention: {e}")
            await message.reply("Sorry, something went wrong. Please try again later.")
    
    async def get_gemini_response(self, question):
        """Get response from Gemini API"""
        if not gemini_client:
            logger.error("Gemini client not initialized")
            return None
        
        try:
            # Create a helpful system prompt for Discord context
            system_prompt = (
                "You are a helpful AI assistant in a Discord server. "
                "Provide clear, concise, and helpful responses to user questions. "
                "Keep responses conversational and friendly, suitable for a chat environment. "
                "If you're unsure about something, be honest about it. "
                "Avoid overly long responses unless specifically asked for detailed explanations."
            )
            
            # Generate response using Gemini
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(
                        role="user", 
                        parts=[types.Part(text=f"{system_prompt}\n\nUser question: {question}")]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1500
                )
            )
            
            if response and response.text:
                logger.info("Successfully generated Gemini response")
                return response.text.strip()
            else:
                logger.warning("Empty response from Gemini")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Gemini response: {e}")
            return None
    
    async def on_error(self, event, *args, **kwargs):
        """Handle bot errors"""
        logger.error(f"Bot error in {event}: {args}", exc_info=True)

# Bot commands
bot = GeminiBot()

@bot.command(name='help')
async def help_command(ctx):
    """Display help information"""
    embed = discord.Embed(
        title="🤖 AI Assistant Bot Help",
        description="I'm an AI-powered bot that can answer your questions!",
        color=0x00ff00
    )
    
    embed.add_field(
        name="How to use:",
        value="Simply mention me (@botname) followed by your question!",
        inline=False
    )
    
    embed.add_field(
        name="Example:",
        value="@botname What is the capital of France?",
        inline=False
    )
    
    embed.add_field(
        name="Features:",
        value="• AI-powered responses using Google Gemini\n• Natural conversation\n• Helpful and informative answers",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='status')
async def status_command(ctx):
    """Check bot status"""
    gemini_status = "✅ Connected" if gemini_client else "❌ Not Connected"
    
    embed = discord.Embed(
        title="🔧 Bot Status",
        color=0x0099ff
    )
    
    embed.add_field(name="Discord", value="✅ Connected", inline=True)
    embed.add_field(name="Gemini AI", value=gemini_status, inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    await ctx.send(embed=embed)

async def main():
    """Main function to run the bot"""
    # Get Discord token from environment
    discord_token = os.environ.get("DISCORD_BOT_TOKEN")
    
    if not discord_token:
        logger.error("DISCORD_BOT_TOKEN environment variable not set")
        return
    
    if not os.environ.get("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY environment variable not set")
        return
    
    try:
        # Start the bot
        await bot.start(discord_token)
    except discord.LoginFailure:
        logger.error("Invalid Discord bot token")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
