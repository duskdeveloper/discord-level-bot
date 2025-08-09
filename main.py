import discord
from discord.ext import commands
import asyncio
import os
import json
from bot.database import Database
from bot.leveling import LevelingSystem
from bot.events import Events
from bot.commands import LevelCommands

class LevelBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.db = Database()
        self.leveling = LevelingSystem(self.db)
        
    async def setup_hook(self):
        await self.db.initialize()
        await self.add_cog(Events(self))
        await self.add_cog(LevelCommands(self))
        
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')
        
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="users level up!"
        )
        await self.change_presence(activity=activity)

async def main():
    bot = LevelBot()
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set")
        return
        
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.close()
    except Exception as e:
        print(f"Error starting bot: {e}")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
