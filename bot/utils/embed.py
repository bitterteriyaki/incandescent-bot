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

from typing import Optional, Union

from discord import Embed, Member, User

from bot.utils.constants import EMBED_COLOR


def create_embed(
    content: Optional[str] = None,
    *,
    author: Union[User, Member],
) -> Embed:
    """Creates an embed with the given content and author, using the
    default embed color.

    Parameters
    ----------
    content: Optional[:class:`str`]
        The content of the embed. If this is not given, then the embed
        will not have any content. Defaults to ``None``.
    author: :class:`discord.Member`
        The author of the embed. This is used to set the author name
        and icon.

    Returns
    -------
    :class:`discord.Embed`
        The embed with the given content and author.
    """
    avatar_url = author.display_avatar.url

    embed = Embed(description=content, color=EMBED_COLOR)
    embed.set_author(name=author.display_name, icon_url=avatar_url)

    return embed
