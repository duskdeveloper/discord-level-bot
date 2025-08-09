import time
import random
import json
import math
from typing import Dict, Optional
from .database import Database

class LevelingSystem:
    def __init__(self, database: Database):
        self.db = database
        self.cooldowns: Dict[str, float] = {}
    
    def calculate_level_from_xp(self, xp: int) -> int:
        if xp < 0:
            return 0
        return int(math.floor(0.1 * math.sqrt(xp)))
    
    def calculate_xp_for_level(self, level: int) -> int:
        return int((level / 0.1) ** 2)
    
    def get_xp_for_next_level(self, current_xp: int) -> int:
        current_level = self.calculate_level_from_xp(current_xp)
        next_level_xp = self.calculate_xp_for_level(current_level + 1)
        return next_level_xp - current_xp
    
    async def should_award_xp(self, user_id: int, guild_id: int) -> bool:
        cooldown_key = f"{user_id}:{guild_id}"
        current_time = time.time()
        
        config = await self.db.get_guild_config(guild_id)
        cooldown_period = config['xp_cooldown']
        
        if cooldown_key in self.cooldowns:
            if current_time - self.cooldowns[cooldown_key] < cooldown_period:
                return False
        
        self.cooldowns[cooldown_key] = current_time
        return True
    
    async def process_message(self, user_id: int, guild_id: int, message_length: int) -> Optional[dict]:
        if not await self.should_award_xp(user_id, guild_id):
            return None
        
        config = await self.db.get_guild_config(guild_id)
        user_data = await self.db.get_user_data(user_id, guild_id)
        
        base_xp = config['xp_per_message']
        length_bonus = min(message_length // 10, 5)
        random_bonus = random.randint(0, 5)
        total_xp = base_xp + length_bonus + random_bonus
        
        old_level = user_data['level']
        new_xp = user_data['xp'] + total_xp
        new_level = self.calculate_level_from_xp(new_xp)
        new_messages = user_data['total_messages'] + 1
        
        await self.db.update_user_data(
            user_id, guild_id, new_xp, new_level, 
            new_messages, time.time()
        )
        
        level_up = new_level > old_level
        
        return {
            'old_level': old_level,
            'new_level': new_level,
            'xp_gained': total_xp,
            'total_xp': new_xp,
            'level_up': level_up,
            'total_messages': new_messages
        }
    
    async def get_level_roles(self, guild_id: int) -> dict:
        config = await self.db.get_guild_config(guild_id)
        try:
            return json.loads(config['level_roles'])
        except (json.JSONDecodeError, TypeError):
            return {}
    
    async def set_level_role(self, guild_id: int, level: int, role_id: int):
        level_roles = await self.get_level_roles(guild_id)
        level_roles[str(level)] = role_id
        
        config = await self.db.get_guild_config(guild_id)
        config['level_roles'] = json.dumps(level_roles)
        await self.db.update_guild_config(guild_id, **config)
    
    async def remove_level_role(self, guild_id: int, level: int):
        level_roles = await self.get_level_roles(guild_id)
        level_roles.pop(str(level), None)
        
        config = await self.db.get_guild_config(guild_id)
        config['level_roles'] = json.dumps(level_roles)
        await self.db.update_guild_config(guild_id, **config)
    
    def format_xp_progress(self, current_xp: int) -> dict:
        current_level = self.calculate_level_from_xp(current_xp)
        level_start_xp = self.calculate_xp_for_level(current_level)
        next_level_xp = self.calculate_xp_for_level(current_level + 1)
        
        progress_xp = current_xp - level_start_xp
        needed_xp = next_level_xp - level_start_xp
        
        return {
            'current_level': current_level,
            'current_xp': current_xp,
            'progress_xp': progress_xp,
            'needed_xp': needed_xp,
            'next_level_total_xp': next_level_xp,
            'percentage': (progress_xp / needed_xp) * 100 if needed_xp > 0 else 100
        }
