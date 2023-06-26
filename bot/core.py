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

from discord import Intents, Message
from discord.ext import commands


class IncandescentBot(commands.Bot):
    """Main bot class. The magic happens here."""

    def __init__(self) -> None:
        intents = Intents.none()
        intents.guilds = True
        intents.messages = True
        intents.message_content = True

        super().__init__(command_prefix=get_prefix, intents=intents)

    async def on_ready(self) -> None:
        assert self.user is not None
        print(f"Logged in as {self.user} ({self.user.id})")


async def get_prefix(bot: IncandescentBot, message: Message) -> str:
    """Get the prefix for the bot.

    Parameters
    ----------
    bot: :class:`IncandescentBot`
        The bot instance.
    message: :class:`discord.Message`
        The message that invoked the command.

    Returns
    -------
    :class:`str`
        The prefix for the message.

    Notes
    -----
    This will be replaced with a database lookup in the future.
    """
    return "in!"
