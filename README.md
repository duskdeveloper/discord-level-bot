# Discord Leveling Bot

## Overview

This is a Discord bot that implements a comprehensive leveling system for Discord servers. Users gain experience points (XP) by sending messages, which translates into levels and ranks within their server. The bot features customizable XP rates, cooldowns, level-up announcements, and provides commands to check user stats and leaderboards. It uses SQLite for data persistence and supports per-guild configuration settings.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py**: Uses the discord.py library with cogs architecture for modular command and event handling
- **Command System**: Implements both traditional prefix commands (!) and modern slash commands using app_commands
- **Event-Driven**: Processes Discord events (messages, guild joins) to award XP and handle level-ups

### Data Storage
- **SQLite Database**: Local file-based database (levelbot.db) for user progression and guild settings
- **Async Database Operations**: Uses aiosqlite for non-blocking database queries
- **Indexed Tables**: Optimized with indexes on user_id/guild_id combinations and XP rankings

### Core Systems

#### Leveling Algorithm
- **XP Calculation**: Mathematical formula using square root progression (level = 0.1 * √XP)
- **Dynamic XP Awards**: Base XP + length bonus + random bonus system
- **Cooldown Management**: In-memory cooldown tracking to prevent XP farming
- **Level Thresholds**: Configurable bronze/silver/gold/platinum/diamond ranks

#### Configuration Management
- **JSON Config**: External config.json for default settings, level thresholds, and UI elements
- **Per-Guild Settings**: Database-stored guild-specific configurations (XP rates, cooldowns, announcements)
- **Runtime Customization**: Admins can modify settings without bot restart

#### User Interface
- **Rich Embeds**: Discord embedded messages with progress bars, thumbnails, and formatted stats
- **Progress Visualization**: ASCII progress bars showing XP progression to next level
- **Emoji Integration**: Configurable emojis for different UI elements
- **Color Coding**: Level-based color schemes and status indicators

### Module Structure
- **main.py**: Bot initialization, event loop, and Discord connection management
- **bot/database.py**: Database abstraction layer with async operations
- **bot/leveling.py**: Core leveling logic, XP calculations, and cooldown management
- **bot/events.py**: Discord event handlers for message processing and level-up announcements
- **bot/commands.py**: Slash command implementations for user interactions
- **bot/utils.py**: Utility functions for formatting, progress bars, and UI helpers

## External Dependencies

### Core Dependencies
- **Discord.py**: Discord API wrapper for bot functionality and real-time event handling
- **aiosqlite**: Async SQLite database driver for non-blocking data operations

### Environment Requirements
- **DISCORD_TOKEN**: Environment variable for bot authentication with Discord API
- **Python 3.8+**: Required for discord.py async features and modern syntax support

### Optional Integrations
- **File System**: Local SQLite database file storage
- **Discord Permissions**: Requires message content intent, guild access, and member intent for full functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.
