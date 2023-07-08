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

import asyncio
from os import environ

import humanize
from click import group

from bot.core import IBot


async def run_bot() -> None:
    humanize.activate("pt_BR")
    token = environ["DISCORD_TOKEN"]

    async with IBot() as bot:
        await bot.start(token)


@group()
def main() -> None:
    pass


@main.command()
def runbot() -> None:
    """Run the bot."""
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
