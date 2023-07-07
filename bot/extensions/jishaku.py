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

from jishaku.features.invocation import InvocationFeature
from jishaku.features.management import ManagementFeature
from jishaku.features.root_command import RootCommand

from bot.core import IBot


class Jishaku(RootCommand, ManagementFeature, InvocationFeature):
    """Custom Jishaku cog. This is used to manage the bot."""

    emote = "<:spfc:1116855346338742363>"


async def setup(bot: IBot) -> None:
    await bot.add_cog(Jishaku(bot=bot))
