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

from discord import Message
from discord.ext.commands import Cog  # type: ignore
from sqlalchemy import insert

from bot.core import IBot
from bot.utils.database import DiscordMessage


class Events(Cog):
    """Handles many Discord events."""

    def __init__(self, bot: IBot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        print(f"Logged in as {self.bot.user}.")

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        async with self.bot.engine.begin() as conn:
            stmt = insert(DiscordMessage).values(
                message_id=message.id,
                author_id=message.author.id,
                channel_id=message.channel.id,
                content=message.content,
                created_at=message.created_at.replace(tzinfo=None),
            )
            await conn.execute(stmt)

        self.bot.dispatch("regular_message", message)


async def setup(bot: IBot) -> None:
    await bot.add_cog(Events(bot))
