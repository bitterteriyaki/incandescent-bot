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
import logging
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from os import environ

from click import group

from bot.core import IncandescentBot


@contextmanager
def setup_logging():
    log = logging.getLogger()

    try:
        # __enter__
        max_bytes = 32 * 1024 * 1024  # 32 MiB

        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.WARN)

        datetime_format = r"%Y-%m-%d %H:%M:%S"
        log_format = "[{asctime}] [{levelname}] {name}: {message}"
        log.setLevel(logging.INFO)

        file_handler = RotatingFileHandler(
            filename="logs/incandescentbot.log",
            encoding="utf-8",
            maxBytes=max_bytes,
            backupCount=5,
        )
        formatter = logging.Formatter(log_format, datetime_format, style="{")

        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

        yield
    finally:
        # __exit__
        for handler in log.handlers:
            handler.close()
            log.removeHandler(handler)


async def run_bot() -> None:
    token = environ["DISCORD_TOKEN"]

    async with IncandescentBot() as bot:
        await bot.start(token)


@group()
def main() -> None:
    pass


@main.command()
def runbot() -> None:
    """Run the bot."""
    with setup_logging():
        asyncio.run(run_bot())


if __name__ == "__main__":
    main()
