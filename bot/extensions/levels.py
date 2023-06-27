"""
Copyright (C) 2023  kyomi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from random import randint
from typing import cast

from discord import Member, Message
from discord.ext import commands
from sqlalchemy import insert, select, update

from bot.core import IncandescentBot
from bot.utils.database import LevelUser
from bot.utils.embed import create_embed


class Levels(commands.Cog):
    """Ranking system for the bot."""

    def __init__(self, bot: IncandescentBot) -> None:
        self.bot = bot
        self.cooldown = commands.CooldownMapping.from_cooldown(
            1, 60, commands.BucketType.user
        )

    def get_level_exp(self, level: int) -> int:
        return 5 * (level**2) + (50 * level) + 100

    def get_level_from_exp(self, exp: int) -> int:
        level = 0

        while exp >= self.get_level_exp(level):
            exp -= self.get_level_exp(level)
            level += 1

        return level

    async def insert_user(self, user_id: int) -> None:
        async with self.bot.engine.begin() as conn:
            stmt = insert(LevelUser).values(user_id=user_id)
            await conn.execute(stmt)

    async def get_experience(
        self, user_id: int, *, insert: bool = False
    ) -> int:
        async with self.bot.engine.begin() as conn:
            stmt = select(LevelUser).where(LevelUser.user_id == user_id)
            result = (await conn.execute(stmt)).fetchone()

        if result is None and insert:
            await self.insert_user(user_id)

        return result.exp if result is not None else 0

    async def add_experience(self, user_id: int, to_add: int) -> int:
        async with self.bot.engine.begin() as conn:
            stmt = (
                update(LevelUser)
                .where(LevelUser.user_id == user_id)
                .values(exp=LevelUser.exp + to_add)
                .returning(LevelUser.exp)
            )
            result = (await conn.execute(stmt)).fetchone()

        return result.exp if result is not None else 0

    @commands.Cog.listener()
    async def on_regular_message(self, message: Message) -> None:
        author = cast(Member, message.author)

        current_exp = await self.get_experience(author.id, insert=True)
        current_level = self.get_level_from_exp(current_exp)

        bucket = self.cooldown.get_bucket(message)
        retry_after = bucket.update_rate_limit() if bucket else None

        if retry_after is not None:
            return

        to_add = randint(15, 25)

        new_exp = await self.add_experience(author.id, to_add)
        new_level = self.get_level_from_exp(new_exp)

        if new_level != current_level:
            content = (
                f"Parabéns, {author.mention}! Você subiu para o "
                f"**nível {new_level}**!"
            )
            embed = create_embed(content, author)

            await message.reply(embed=embed, mention_author=False)


async def setup(bot: IncandescentBot) -> None:
    await bot.add_cog(Levels(bot))
