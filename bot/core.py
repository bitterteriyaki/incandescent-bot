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

import logging
from os import environ
from typing import Any, Type, Union, cast

from aiohttp import ClientSession
from discord import Game, Guild, Intents, Interaction, Message, Status
from discord.ext.commands import Bot, Context  # type: ignore
from discord.utils import cached_property, setup_logging
from jishaku.modules import find_extensions_in
from sqlalchemy.ext.asyncio import create_async_engine

from bot.utils.constants import GUILD_ID
from bot.utils.context import IContext
from bot.utils.database import DB_URL

environ["JISHAKU_NO_UNDERSCORE"] = "true"
environ["JISHAKU_NO_DM_TRACEBACK"] = "true"

log = logging.getLogger(__name__)


class IBot(Bot):
    """Main bot class. The magic happens here."""

    def __init__(self) -> None:
        super().__init__(
            command_prefix=get_prefix,
            intents=Intents.all(),
            activity=Game(name="discord.gg/incandescent"),
            status=Status.dnd,
        )

        self.default_prefix = "in?" if self.env == "development" else "in!"
        self.engine = create_async_engine(DB_URL)
        self.session = ClientSession()

        setup_logging()

    async def setup_hook(self) -> None:
        for extension in find_extensions_in("bot/extensions"):
            await self.load_extension(extension)

    async def get_context(
        self,
        origin: Union[Message, Interaction],
        /,
        *,
        cls: Type[Context[Any]] = IContext,
    ) -> Any:
        return await super().get_context(origin, cls=cls)

    @cached_property
    def guild(self) -> Guild:
        return cast(Guild, self.get_guild(GUILD_ID))

    @cached_property
    def env(self) -> str:
        return (
            "development"
            if environ["BOT_ENV"] == "development"
            else "production"
        )


async def get_prefix(bot: IBot, message: Message) -> str:
    """Get the prefix for the bot.

    Parameters
    ----------
    bot: :class:`IBot`
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
