import discord
from discord.ext import commands
import json

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        if len(message.content) < 3:
            return
        
        try:
            result = await self.bot.leveling.process_message(
                message.author.id,
                message.guild.id,
                len(message.content)
            )
            
            if result and result['level_up']:
                await self.handle_level_up(message, result)
                
        except Exception as e:
            print(f"Error processing message XP: {e}")
    
    async def handle_level_up(self, message, result):
        try:
            config = await self.bot.db.get_guild_config(message.guild.id)
            
            if not config['announcement_enabled']:
                return
            
            new_level = result['new_level']
            user = message.author
            
            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"{user.mention} has reached **Level {new_level}**!",
                color=0x00ff00
            )
            
            embed.add_field(
                name="Total XP",
                value=f"{result['total_xp']:,}",
                inline=True
            )
            
            embed.add_field(
                name="Messages Sent",
                value=f"{result['total_messages']:,}",
                inline=True
            )
            
            embed.set_thumbnail(url=user.display_avatar.url)
            
            channel = message.channel
            if config['level_up_channel']:
                channel = self.bot.get_channel(config['level_up_channel'])
                if not channel:
                    channel = message.channel
            
            await channel.send(embed=embed)
            
            await self.assign_level_roles(user, message.guild, new_level)
            
        except Exception as e:
            print(f"Error handling level up: {e}")
    
    async def assign_level_roles(self, user, guild, new_level):
        try:
            level_roles = await self.bot.leveling.get_level_roles(guild.id)
            
            for level_str, role_id in level_roles.items():
                level = int(level_str)
                role = guild.get_role(role_id)
                
                if not role:
                    continue
                
                if level <= new_level:
                    if role not in user.roles:
                        await user.add_roles(role, reason=f"Reached level {level}")
                else:
                    if role in user.roles:
                        await user.remove_roles(role, reason=f"Below level {level}")
                        
        except Exception as e:
            print(f"Error assigning level roles: {e}")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            config = await self.bot.db.get_guild_config(guild.id)
            if not config:
                await self.bot.db.update_guild_config(guild.id)
                
        except Exception as e:
            print(f"Error setting up new guild: {e}")
