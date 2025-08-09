import discord
from discord.ext import commands
from discord import app_commands
import json
from .utils import create_progress_bar

class LevelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="rank", description="Check your current level and XP")
    @app_commands.describe(user="User to check rank for (optional)")
    async def rank(self, interaction: discord.Interaction, user: discord.Member = None):
        target_user = user or interaction.user
        
        if target_user.bot:
            await interaction.response.send_message("Bots don't have levels!", ephemeral=True)
            return
        
        try:
            user_data = await self.bot.db.get_user_data(target_user.id, interaction.guild.id)
            rank = await self.bot.db.get_user_rank(target_user.id, interaction.guild.id)
            progress = self.bot.leveling.format_xp_progress(user_data['xp'])
            
            embed = discord.Embed(
                title=f"📊 {target_user.display_name}'s Stats",
                color=0x3498db
            )
            
            embed.set_thumbnail(url=target_user.display_avatar.url)
            
            embed.add_field(
                name="Level",
                value=f"**{progress['current_level']}**",
                inline=True
            )
            
            embed.add_field(
                name="Rank",
                value=f"#{rank}",
                inline=True
            )
            
            embed.add_field(
                name="Total XP",
                value=f"{user_data['xp']:,}",
                inline=True
            )
            
            embed.add_field(
                name="Messages",
                value=f"{user_data['total_messages']:,}",
                inline=True
            )
            
            embed.add_field(
                name="Progress to Next Level",
                value=f"{progress['progress_xp']:,} / {progress['needed_xp']:,} XP",
                inline=True
            )
            
            embed.add_field(
                name="Progress Bar",
                value=create_progress_bar(progress['percentage']),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message("An error occurred while fetching rank data.", ephemeral=True)
    
    @app_commands.command(name="leaderboard", description="View the server leaderboard")
    @app_commands.describe(page="Page number (optional)")
    async def leaderboard(self, interaction: discord.Interaction, page: int = 1):
        try:
            page = max(1, page)
            limit = 10
            offset = (page - 1) * limit
            
            leaderboard_data = await self.bot.db.get_leaderboard(interaction.guild.id, limit + offset)
            
            if not leaderboard_data:
                await interaction.response.send_message("No users found in the leaderboard!", ephemeral=True)
                return
            
            page_data = leaderboard_data[offset:offset + limit]
            
            embed = discord.Embed(
                title=f"🏆 Server Leaderboard - Page {page}",
                color=0xffd700
            )
            
            description = ""
            for i, (user_id, xp, level, messages) in enumerate(page_data, start=offset + 1):
                user = self.bot.get_user(user_id)
                username = user.display_name if user else f"User {user_id}"
                
                medal = ""
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"**{i}.**"
                
                description += f"{medal} {username}\n"
                description += f"Level {level} • {xp:,} XP • {messages:,} messages\n\n"
            
            embed.description = description
            
            total_pages = (len(leaderboard_data) + limit - 1) // limit
            embed.set_footer(text=f"Page {page} of {total_pages}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message("An error occurred while fetching leaderboard data.", ephemeral=True)
    
    @app_commands.command(name="addxp", description="Add XP to a user (Admin only)")
    @app_commands.describe(user="User to add XP to", amount="Amount of XP to add")
    @app_commands.default_permissions(administrator=True)
    async def add_xp(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if user.bot:
            await interaction.response.send_message("Cannot modify bot XP!", ephemeral=True)
            return
        
        if amount <= 0:
            await interaction.response.send_message("XP amount must be positive!", ephemeral=True)
            return
        
        try:
            old_data = await self.bot.db.get_user_data(user.id, interaction.guild.id)
            await self.bot.db.add_xp(user.id, interaction.guild.id, amount)
            new_data = await self.bot.db.get_user_data(user.id, interaction.guild.id)
            
            old_level = self.bot.leveling.calculate_level_from_xp(old_data['xp'])
            new_level = self.bot.leveling.calculate_level_from_xp(new_data['xp'])
            
            embed = discord.Embed(
                title="✅ XP Added",
                description=f"Added {amount:,} XP to {user.mention}",
                color=0x00ff00
            )
            
            embed.add_field(
                name="Old Level",
                value=str(old_level),
                inline=True
            )
            
            embed.add_field(
                name="New Level",
                value=str(new_level),
                inline=True
            )
            
            embed.add_field(
                name="Total XP",
                value=f"{new_data['xp']:,}",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message("An error occurred while adding XP.", ephemeral=True)
    
    @app_commands.command(name="setxp", description="Set a user's XP (Admin only)")
    @app_commands.describe(user="User to set XP for", amount="XP amount to set")
    @app_commands.default_permissions(administrator=True)
    async def set_xp(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if user.bot:
            await interaction.response.send_message("Cannot modify bot XP!", ephemeral=True)
            return
        
        if amount < 0:
            await interaction.response.send_message("XP amount cannot be negative!", ephemeral=True)
            return
        
        try:
            await self.bot.db.set_xp(user.id, interaction.guild.id, amount)
            new_level = self.bot.leveling.calculate_level_from_xp(amount)
            
            embed = discord.Embed(
                title="✅ XP Set",
                description=f"Set {user.mention}'s XP to {amount:,}",
                color=0x00ff00
            )
            
            embed.add_field(
                name="New Level",
                value=str(new_level),
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message("An error occurred while setting XP.", ephemeral=True)
    
    @app_commands.command(name="config", description="Configure leveling system (Admin only)")
    @app_commands.describe(
        xp_per_message="XP awarded per message",
        cooldown="Cooldown between XP awards (seconds)",
        announcement_channel="Channel for level up announcements",
        announcements="Enable/disable level up announcements"
    )
    @app_commands.default_permissions(administrator=True)
    async def config(self, interaction: discord.Interaction, 
                    xp_per_message: int = None,
                    cooldown: int = None,
                    announcement_channel: discord.TextChannel = None,
                    announcements: bool = None):
        try:
            config = await self.bot.db.get_guild_config(interaction.guild.id)
            
            if xp_per_message is not None:
                if xp_per_message <= 0 or xp_per_message > 100:
                    await interaction.response.send_message("XP per message must be between 1 and 100!", ephemeral=True)
                    return
                config['xp_per_message'] = xp_per_message
            
            if cooldown is not None:
                if cooldown < 0 or cooldown > 3600:
                    await interaction.response.send_message("Cooldown must be between 0 and 3600 seconds!", ephemeral=True)
                    return
                config['xp_cooldown'] = cooldown
            
            if announcement_channel is not None:
                config['level_up_channel'] = announcement_channel.id
            
            if announcements is not None:
                config['announcement_enabled'] = 1 if announcements else 0
            
            await self.bot.db.update_guild_config(interaction.guild.id, **config)
            
            embed = discord.Embed(
                title="⚙️ Configuration Updated",
                color=0x3498db
            )
            
            embed.add_field(
                name="XP per Message",
                value=str(config['xp_per_message']),
                inline=True
            )
            
            embed.add_field(
                name="Cooldown",
                value=f"{config['xp_cooldown']}s",
                inline=True
            )
            
            channel_name = "Current Channel"
            if config['level_up_channel']:
                channel = self.bot.get_channel(config['level_up_channel'])
                if channel:
                    channel_name = channel.mention
            
            embed.add_field(
                name="Announcement Channel",
                value=channel_name,
                inline=True
            )
            
            embed.add_field(
                name="Announcements",
                value="Enabled" if config['announcement_enabled'] else "Disabled",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message("An error occurred while updating configuration.", ephemeral=True)
    
    @app_commands.command(name="levelrole", description="Manage level roles (Admin only)")
    @app_commands.describe(
        action="Action to perform",
        level="Level requirement",
        role="Role to assign"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="list", value="list")
    ])
    @app_commands.default_permissions(administrator=True)
    async def level_role(self, interaction: discord.Interaction, 
                        action: str, level: int = None, role: discord.Role = None):
        try:
            if action == "list":
                level_roles = await self.bot.leveling.get_level_roles(interaction.guild.id)
                
                if not level_roles:
                    await interaction.response.send_message("No level roles configured!", ephemeral=True)
                    return
                
                embed = discord.Embed(
                    title="🎭 Level Roles",
                    color=0x9b59b6
                )
                
                description = ""
                for level_str, role_id in sorted(level_roles.items(), key=lambda x: int(x[0])):
                    role_obj = interaction.guild.get_role(role_id)
                    role_name = role_obj.mention if role_obj else f"Deleted Role ({role_id})"
                    description += f"Level {level_str}: {role_name}\n"
                
                embed.description = description
                await interaction.response.send_message(embed=embed)
                
            elif action == "add":
                if level is None or role is None:
                    await interaction.response.send_message("Level and role are required for adding!", ephemeral=True)
                    return
                
                if level <= 0:
                    await interaction.response.send_message("Level must be positive!", ephemeral=True)
                    return
                
                await self.bot.leveling.set_level_role(interaction.guild.id, level, role.id)
                
                embed = discord.Embed(
                    title="✅ Level Role Added",
                    description=f"Users will receive {role.mention} at level {level}",
                    color=0x00ff00
                )
                
                await interaction.response.send_message(embed=embed)
                
            elif action == "remove":
                if level is None:
                    await interaction.response.send_message("Level is required for removing!", ephemeral=True)
                    return
                
                await self.bot.leveling.remove_level_role(interaction.guild.id, level)
                
                embed = discord.Embed(
                    title="✅ Level Role Removed",
                    description=f"Removed level role for level {level}",
                    color=0x00ff00
                )
                
                await interaction.response.send_message(embed=embed)
                
        except Exception as e:
            await interaction.response.send_message("An error occurred while managing level roles.", ephemeral=True)
