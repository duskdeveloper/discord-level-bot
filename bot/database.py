import sqlite3
import asyncio
import aiosqlite
from typing import List, Tuple, Optional

class Database:
    def __init__(self, db_path: str = "levelbot.db"):
        self.db_path = db_path
        
    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_levels (
                    user_id INTEGER,
                    guild_id INTEGER,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    last_message_time REAL DEFAULT 0,
                    PRIMARY KEY (user_id, guild_id)
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS guild_config (
                    guild_id INTEGER PRIMARY KEY,
                    xp_per_message INTEGER DEFAULT 15,
                    xp_cooldown INTEGER DEFAULT 60,
                    level_up_channel INTEGER,
                    level_roles TEXT DEFAULT '{}',
                    announcement_enabled INTEGER DEFAULT 1
                )
            ''')
            
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_guild ON user_levels(user_id, guild_id)
            ''')
            
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_guild_xp ON user_levels(guild_id, xp DESC)
            ''')
            
            await db.commit()
    
    async def get_user_data(self, user_id: int, guild_id: int) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT xp, level, total_messages, last_message_time
                FROM user_levels
                WHERE user_id = ? AND guild_id = ?
            ''', (user_id, guild_id))
            
            row = await cursor.fetchone()
            if row:
                return {
                    'xp': row[0],
                    'level': row[1],
                    'total_messages': row[2],
                    'last_message_time': row[3]
                }
            return {
                'xp': 0,
                'level': 0,
                'total_messages': 0,
                'last_message_time': 0
            }
    
    async def update_user_data(self, user_id: int, guild_id: int, xp: int, level: int, 
                              total_messages: int, last_message_time: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO user_levels 
                (user_id, guild_id, xp, level, total_messages, last_message_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, guild_id, xp, level, total_messages, last_message_time))
            await db.commit()
    
    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> List[Tuple]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT user_id, xp, level, total_messages
                FROM user_levels
                WHERE guild_id = ?
                ORDER BY xp DESC
                LIMIT ?
            ''', (guild_id, limit))
            
            return await cursor.fetchall()
    
    async def get_user_rank(self, user_id: int, guild_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT COUNT(*) + 1
                FROM user_levels
                WHERE guild_id = ? AND xp > (
                    SELECT xp FROM user_levels
                    WHERE user_id = ? AND guild_id = ?
                )
            ''', (guild_id, user_id, guild_id))
            
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def get_guild_config(self, guild_id: int) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT xp_per_message, xp_cooldown, level_up_channel, 
                       level_roles, announcement_enabled
                FROM guild_config
                WHERE guild_id = ?
            ''', (guild_id,))
            
            row = await cursor.fetchone()
            if row:
                return {
                    'xp_per_message': row[0],
                    'xp_cooldown': row[1],
                    'level_up_channel': row[2],
                    'level_roles': row[3],
                    'announcement_enabled': row[4]
                }
            
            return {
                'xp_per_message': 15,
                'xp_cooldown': 60,
                'level_up_channel': None,
                'level_roles': '{}',
                'announcement_enabled': 1
            }
    
    async def update_guild_config(self, guild_id: int, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO guild_config 
                (guild_id, xp_per_message, xp_cooldown, level_up_channel, 
                 level_roles, announcement_enabled)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                guild_id,
                kwargs.get('xp_per_message', 15),
                kwargs.get('xp_cooldown', 60),
                kwargs.get('level_up_channel'),
                kwargs.get('level_roles', '{}'),
                kwargs.get('announcement_enabled', 1)
            ))
            await db.commit()
    
    async def add_xp(self, user_id: int, guild_id: int, amount: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE user_levels
                SET xp = xp + ?
                WHERE user_id = ? AND guild_id = ?
            ''', (amount, user_id, guild_id))
            await db.commit()
    
    async def set_xp(self, user_id: int, guild_id: int, amount: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO user_levels 
                (user_id, guild_id, xp, level, total_messages, last_message_time)
                VALUES (?, ?, ?, 0, 0, 0)
            ''', (user_id, guild_id, amount))
            await db.commit()
