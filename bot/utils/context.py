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

from typing import TYPE_CHECKING, Any, Optional

from discord import Message
from discord.ext import commands

from bot.utils.embed import create_embed

if TYPE_CHECKING:
    from bot.core import IBot
else:
    IBot = Any


class IContext(commands.Context[IBot]):
    """A subclass of :class:`discord.ext.commands.Context` that
    overrides some methods and adds some new ones. This is used as the
    context for all commands in the bot.
    """

    async def reply(
        self,
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> Message:
        """Overrides :meth:`discord.ext.commands.Context.reply` to
        automatically create an embed with the given content and author
        and reply with that embed.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The content of the reply. If this is not given, then the
            reply will not have any content. Defaults to ``None``.
        **kwargs: Any
            Any keyword arguments to pass to
            :meth:`discord.ext.commands.Context.reply`. This is passed
            to :meth:`discord.abc.Messageable.send`.
        """
        mention_author = kwargs.pop("mention_author", False)
        embed = kwargs.pop("embed", create_embed(content, author=self.author))

        return await super().reply(
            embed=embed, mention_author=mention_author, **kwargs
        )
