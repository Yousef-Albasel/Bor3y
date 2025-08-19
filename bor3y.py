import logging
import aiosqlite
import discord
import asyncio
from discord.ext import commands
from ai_client import *
from discord import app_commands
from datetime import datetime
from reminder_db import init_db, add_reminder, get_due_reminders, delete_reminder
from task_db import init_task_db, add_task, delete_task, get_all_tasks
from zoneinfo import ZoneInfo
logger = logging.getLogger(__name__)
gemini_llm = get_gemini_llm()

class Bor3yBot(commands.Bot):
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
        self.bg_task = None

    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="السيرفر | Server Guardian"
        )
        await self.change_presence(activity=activity)
    async def setup_hook(self):
            await init_db()
            await init_task_db()
            await self.tree.sync()  # Sync slash commands on startup
            self.bg_task = asyncio.create_task(self.reminder_loop())

    async def reminder_loop(self):
        await self.wait_until_ready()
        while not self.is_closed():
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            due = await get_due_reminders(now)
            for reminder in due:
                _id, user_id, channel_id, message, when_utc = reminder
                channel = self.get_channel(channel_id)
                if channel:
                    try:
                        await channel.send(f"⏰ <@everyone> Reminder: {message} (scheduled for {when_utc} UTC)")
                    except Exception as e:
                        logger.error(f"Failed to send reminder: {e}")
                await delete_reminder(_id)
            await asyncio.sleep(60)

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
                    await message.reply("أهلاً! أنا برعي، بواب السيرفر. اسأل سؤالك وسأساعدك بإجابة ذكية!\nHi! I'm Bor3y, the Server Gatekeeper. Ask me a question and I'll help you with an AI-generated response!")
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
            prompt = build_prompt(question)
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

bot = Bor3yBot()

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

@bot.tree.command(name="search", description="Search the web and answer using Gemini")
@app_commands.describe(query="Your search query")
async def search_command(interaction: discord.Interaction, query: str):
    try:
        await interaction.response.defer(thinking=True)
        qa_chain = get_search_chain()
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: qa_chain.invoke(query))
        answer = response['result']
        sources = response.get('source_documents', [])
        sources_text = "\n".join([f"[{doc.metadata.get('title','Source')}]({doc.metadata.get('source','')})" for doc in sources])
        truncated_sources = sources_text
        if len(truncated_sources) > 1024:
            truncated_sources = truncated_sources[:1020] + "..."

        embed = discord.Embed(
            title="Search Results",
            description=answer,
            color=0x0099ff
        )
        if truncated_sources:
            embed.add_field(name="Sources", value=truncated_sources, inline=False)
        else:
            embed.add_field(name="Sources", value="No sources found.", inline=False)
        await interaction.followup.send(embed=embed)

        if len(sources_text) > 1024:
            chunks = [sources_text[i:i+2000] for i in range(0, len(sources_text), 2000)]
            for chunk in chunks:
                await interaction.followup.send(chunk)
    except Exception as e:
        logger.error(f"Error in search command: {e}")
        await interaction.followup.send("Sorry, I couldn't perform the search. Please try again later.")

@bot.tree.command(name="schedule", description="Schedule a message to be sent later (Cairo Time)")
@app_commands.describe(
    message="The message to send",
    time="When to send it (YYYY-MM-DD HH:MM, 24h Cairo time)"
)
async def schedule_command(interaction: discord.Interaction, message: str, time: str):
    try:
        await interaction.response.defer(thinking=True)
        try:
            # Parse as Cairo time
            cairo = ZoneInfo("Africa/Cairo")
            when_cairo = datetime.strptime(time, "%Y-%m-%d %H:%M").replace(tzinfo=cairo)
            when_utc = when_cairo.astimezone(ZoneInfo("UTC"))
        except Exception:
            await interaction.followup.send("Invalid time format. Use YYYY-MM-DD HH:MM (24h Cairo time).")
            return
        await add_reminder(
            user_id=interaction.user.id,
            channel_id=interaction.channel_id,
            message=message,
            when_utc=when_utc.strftime("%Y-%m-%d %H:%M")
        )
        await interaction.followup.send(
            f"Message scheduled for {when_cairo.strftime('%Y-%m-%d %H:%M')} Cairo time "
            f"({when_utc.strftime('%Y-%m-%d %H:%M')} UTC)!"
        )
    except Exception as e:
        logger.error(f"Error in schedule command: {e}")
        await interaction.followup.send("Sorry, I couldn't schedule your message.")

@bot.tree.command(name="scheduled", description="Show all your scheduled messages (Cairo Time)")
async def scheduled_command(interaction: discord.Interaction):
    try:
        await interaction.response.defer(thinking=True)
        async with aiosqlite.connect("reminders.db") as db:
            cursor = await db.execute(
                "SELECT message, when_utc FROM reminders WHERE user_id = ? AND channel_id = ?",
                (interaction.user.id, interaction.channel_id)
            )
            rows = await cursor.fetchall()
        if not rows:
            await interaction.followup.send("You have no scheduled messages in this channel.")
            return

        cairo = ZoneInfo("Africa/Cairo")
        lines = []
        for msg, when_utc in rows:
            when_utc_dt = datetime.strptime(when_utc, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo("UTC"))
            when_cairo = when_utc_dt.astimezone(cairo).strftime("%Y-%m-%d %H:%M")
            lines.append(f"**{when_cairo} Cairo:** {msg}")

        output = "\n".join(lines)
        if len(output) > 2000:
            with open("scheduled.txt", "w", encoding="utf-8") as f:
                f.write(output)
            file = discord.File("scheduled.txt")
            await interaction.followup.send("Your scheduled messages:", file=file)
        else:
            await interaction.followup.send(f"Your scheduled messages:\n{output}")

    except Exception as e:
        logger.error(f"Error in scheduled command: {e}")
        await interaction.followup.send("Sorry, I couldn't retrieve your scheduled messages.")

@bot.tree.command(name="assign", description="Assign a task to a user")
@app_commands.describe(
    user="The user to assign the task to",
    task="The task description"
)
async def assign_command(interaction: discord.Interaction, user: discord.Member, task: str):
    try:
        await add_task(
            assigner_id=interaction.user.id,
            assignee_id=user.id,
            channel_id=interaction.channel_id,
            task=task
        )
        await interaction.response.send_message(
            f"✅ Task assigned to {user.mention}: {task}", ephemeral=False
        )
    except Exception as e:
        logger.error(f"Error in assign command: {e}")
        await interaction.response.send_message("Sorry, I couldn't assign the task.")

@bot.tree.command(name="delete_task", description="Delete a task by its ID")
@app_commands.describe(
    task_id="The ID of the task to delete"
)
async def delete_task_command(interaction: discord.Interaction, task_id: int):
    try:
        await delete_task(task_id)
        await interaction.response.send_message(f"🗑️ Task {task_id} deleted.", ephemeral=False)
    except Exception as e:
        logger.error(f"Error in delete_task command: {e}")
        await interaction.response.send_message("Sorry, I couldn't delete the task.")
@bot.tree.command(name="tasks", description="View all assigned tasks")
async def tasks_command(interaction: discord.Interaction):
    try:
        await interaction.response.defer(thinking=True)
        tasks = await get_all_tasks()
        if not tasks:
            await interaction.followup.send("No tasks assigned yet.")
            return

        from collections import defaultdict
        user_tasks = defaultdict(list)
        for task_id, assigner_id, assignee_id, channel_id, task_desc in tasks:
            user_tasks[assignee_id].append((task_id, assigner_id, channel_id, task_desc))

        embeds = []
        for assignee_id, task_list in user_tasks.items():
            # Try to get the member from cache, else fetch from API
            user = interaction.guild.get_member(assignee_id)
            if user is None:
                try:
                    user = await interaction.guild.fetch_member(assignee_id)
                except Exception:
                    user = None

            if user:
                name = user.display_name
                icon_url = user.display_avatar.url
            else:
                name = f"User {assignee_id}"
                icon_url = None

            value = ""
            for task_id, assigner_id, channel_id, task_desc in task_list:
                line = f"**#{task_id}**: {task_desc} _(by <@{assigner_id}> in <#{channel_id}>)_\n"
                if len(value) + len(line) > 1024:
                    value += "... (truncated)\n"
                    break
                value += line

            embed = discord.Embed(
                title=f"📋 Tasks for {name}",
                description=value or "No tasks.",
                color=0x3498db
            )
            if icon_url:
                embed.set_author(name=name, icon_url=icon_url)
            else:
                embed.set_author(name=name)
            embed.set_footer(text="Task IDs shown for easy reference.")
            embeds.append(embed)

        for i in range(0, len(embeds), 10):
            await interaction.followup.send(embeds=embeds[i:i+10])

    except Exception as e:
        logger.error(f"Error in tasks command: {e}")
        await interaction.followup.send("Sorry, I couldn't retrieve the tasks.")
