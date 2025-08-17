import os
import logging
import asyncio
import discord
from discord.ext import commands
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import dotenv

dotenv.load_dotenv()
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

# Initialize Gemini client using LangChain
try:
    gemini_llm = ChatGoogleGenerativeAI(
        google_api_key=os.environ.get("GEMINI_API_KEY"),
        model="gemini-1.5-flash",
        temperature=0.7,
        max_output_tokens=1500
    )
    logger.info("Gemini LLM initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini LLM: {e}")
    gemini_llm = None

# LangChain prompt template
system_prompt = (
    "You are an AI assistant named 'برعي' (Borai) and your job title is 'بواب السيرفر' (Server Gatekeeper). "
    "When introducing yourself, mention you are برعي بواب السيرفر. "
    "IMPORTANT: Always respond in English unless the user specifically asks you to respond in Arabic. "
    "Even if the user asks questions in Arabic, respond in English unless they explicitly request Arabic responses. "
    "Provide clear, concise, and helpful responses to user questions. "
    "Keep responses conversational and friendly, suitable for a chat environment. "
    "If you're unsure about something, be honest about it. "
    "Maintain your identity as the server gatekeeper but prioritize English communication.\n\n"
    "User question: {question}"
)
prompt_template = PromptTemplate(
    input_variables=["question"],
    template=system_prompt
)

class GeminiBot(commands.Bot):
    def __init__(self):
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
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="السيرفر | Server Guardian"
        )
        await self.change_presence(activity=activity)
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        if self.user in message.mentions:
            await self.handle_mention(message)
        await self.process_commands(message)
    
    async def handle_mention(self, message):
        try:
            async with message.channel.typing():
                content = message.content
                for mention in message.mentions:
                    content = content.replace(f'<@{mention.id}>', '').strip()
                    content = content.replace(f'<@!{mention.id}>', '').strip()
                if not content:
                    await message.reply("أهلاً! أنا برعي، بواب السيرفر. اسأل سؤالك وسأساعدك بإجابة ذكية!\nHi! I'm Borai, the Server Gatekeeper. Ask me a question and I'll help you with an AI-generated response!")
                    return
                logger.info(f"Processing question from {message.author}: {content}")
                ai_response = await self.get_gemini_response(content)
                if ai_response:
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
        if not gemini_llm:
            logger.error("Gemini LLM not initialized")
            return None
        try:
            prompt = prompt_template.format(question=question)
            # LangChain LLMs are synchronous, so run in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: gemini_llm.invoke(prompt)
            )
            if hasattr(response, "content"):
                text = response.content.strip()
            else:
                text = str(response).strip()
            logger.info("Successfully generated Gemini response")
            return text
        except Exception as e:
            logger.error(f"Error getting Gemini response: {e}")
            return None
    
    async def on_error(self, event, *args, **kwargs):
        logger.error(f"Bot error in {event}: {args}", exc_info=True)

bot = GeminiBot()

@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(
        title="🤖 برعي - بواب السيرفر",
        description="أنا برعي، بواب السيرفر! مساعد ذكي يمكنه الإجابة على أسئلتكم\nI'm Borai, the Server Gatekeeper! An AI assistant that can answer your questions",
        color=0x00ff00
    )
    embed.add_field(
        name="كيفية الاستخدام / How to use:",
        value="اذكرني (@برعي) متبوعاً بسؤالك!\nSimply mention me (@Borai) followed by your question!",
        inline=False
    )
    embed.add_field(
        name="مثال / Example:",
        value="@برعي ما هي عاصمة فرنسا؟\n@Borai What is the capital of France?",
        inline=False
    )
    embed.add_field(
        name="المميزات / Features:",
        value="• إجابات ذكية باستخدام Google Gemini / AI-powered responses\n• محادثة طبيعية / Natural conversation\n• إجابات مفيدة ومعلوماتية / Helpful and informative answers\n• يدعم العربية والإنجليزية / Supports Arabic and English",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command(name='status')
async def status_command(ctx):
    gemini_status = "✅ Connected" if gemini_llm else "❌ Not Connected"
    embed = discord.Embed(
        title="🔧 Bot Status",
        color=0x0099ff
    )
    embed.add_field(name="Discord", value="✅ Connected", inline=True)
    embed.add_field(name="Gemini AI", value=gemini_status, inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    await ctx.send(embed=embed)

async def main():
    discord_token = os.environ.get("DISCORD_BOT_TOKEN")
    if not discord_token:
        logger.error("DISCORD_BOT_TOKEN environment variable not set")
        return
    if not os.environ.get("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY environment variable not set")
        return
    try:
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