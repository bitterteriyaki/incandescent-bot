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

from os import environ
from typing import Any, Type, Union, cast

from discord import ClientUser, Guild, Intents, Interaction, Message, Webhook
from discord.ext import commands
from discord.utils import cached_property
from sqlalchemy.ext.asyncio import create_async_engine

from bot.utils.constants import GUILD_ID
from bot.utils.context import IncandescentContext
from bot.utils.database import DB_URL
from bot.utils.extensions import get_extensions

environ["JISHAKU_NO_UNDERSCORE"] = "true"
environ["JISHAKU_NO_DM_TRACEBACK"] = "true"


class IncandescentBot(commands.Bot):
    """Main bot class. The magic happens here."""

    def __init__(self) -> None:
        super().__init__(command_prefix=get_prefix, intents=Intents.all())

        self.default_prefix = "in!"
        self.engine = create_async_engine(DB_URL)

    async def setup_hook(self) -> None:
        for extension in get_extensions():
            await self.load_extension(extension)

        await self.load_extension("jishaku")

    async def get_context(
        self,
        origin: Union[Message, Interaction],
        /,
        *,
        cls: Type[commands.Context[Any]] = IncandescentContext,
    ) -> Any:
        return await super().get_context(origin, cls=cls)

    async def on_ready(self) -> None:
        user = cast(ClientUser, self.user)
        print(f"Logged in as {user} ({user.id})")

    async def on_message(self, message: Message) -> None:
        author = message.author

        if author.bot or isinstance(author, Webhook):
            return

        self.dispatch("regular_message", message)
        await self.process_commands(message)

    @cached_property
    def guild(self) -> Guild:
        return cast(Guild, self.get_guild(GUILD_ID))

    @cached_property
    def env(self) -> str:
        return environ["BOT_ENV"]


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
    return bot.default_prefix
