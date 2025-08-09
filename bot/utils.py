import discord
from typing import Union

def create_progress_bar(percentage: float, length: int = 20) -> str:
    filled = int(length * percentage / 100)
    empty = length - filled
    
    bar = "█" * filled + "░" * empty
    return f"`{bar}` {percentage:.1f}%"

def format_number(number: int) -> str:
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)

def calculate_reading_time(text: str) -> int:
    words = len(text.split())
    return max(1, words // 200)

def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def get_level_color(level: int) -> int:
    colors = [
        0x95a5a6,  # Gray (0-9)
        0x3498db,  # Blue (10-19)
        0x2ecc71,  # Green (20-29)
        0xf39c12,  # Orange (30-39)
        0xe74c3c,  # Red (40-49)
        0x9b59b6,  # Purple (50-59)
        0xffd700,  # Gold (60+)
    ]
    
    color_index = min(level // 10, len(colors) - 1)
    return colors[color_index]

def format_time_delta(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    elif seconds < 86400:
        return f"{seconds // 3600}h"
    else:
        return f"{seconds // 86400}d"

def create_embed_field_chunks(text: str, max_length: int = 1024) -> list:
    chunks = []
    current_chunk = ""
    
    lines = text.split('\n')
    for line in lines:
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + '\n'
        else:
            if current_chunk:
                chunks.append(current_chunk.rstrip())
            current_chunk = line + '\n'
    
    if current_chunk:
        chunks.append(current_chunk.rstrip())
    
    return chunks

def validate_xp_amount(amount: Union[int, str]) -> tuple[bool, int]:
    try:
        xp = int(amount)
        if xp < 0:
            return False, 0
        if xp > 10_000_000:
            return False, 0
        return True, xp
    except (ValueError, TypeError):
        return False, 0

def get_next_milestone(level: int) -> int:
    milestones = [5, 10, 25, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
    
    for milestone in milestones:
        if level < milestone:
            return milestone
    
    return ((level // 100) + 1) * 100
