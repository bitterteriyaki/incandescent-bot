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

from datetime import timedelta
from typing import Optional

from discord import Message
from discord.ext.commands import Cog  # type: ignore
from discord.ext.commands.errors import (  # type: ignore
    CommandError,
    CommandOnCooldown,
)
from humanize import precisedelta

from bot.core import IBot
from bot.utils.context import IContext


class Errors(Cog):
    """Handles errors raised by commands. In the future, this will
    create tickets for the developers to see what went wrong. For now,
    it just sends the error to the console.
    """

    def __init__(self, bot: IBot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_command_error(
        self, ctx: IContext, exception: CommandError
    ) -> Optional[Message]:
        if isinstance(exception, CommandOnCooldown):
            delta = timedelta(seconds=exception.retry_after)
            retry_after = precisedelta(delta, format="%0.0f")

            message = (
                f"Você só poderá usar este comando novamente em "
                f"**{retry_after}**."
            )

            return await ctx.reply(message)

        raise exception


async def setup(bot: IBot) -> None:
    await bot.add_cog(Errors(bot))
