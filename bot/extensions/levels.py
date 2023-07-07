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

from random import randint
from typing import Dict, cast

from discord import Member, Message, Role, TextChannel
from discord.ext import commands
from discord.ext.commands import (  # type: ignore
    BucketType,
    Cog,
    CooldownMapping,
)
from sqlalchemy import insert, select, update

from bot.core import IBot
from bot.utils.constants import LEVELS_MAPPING, TEST_CHANNEL_ID
from bot.utils.database import LevelUser
from bot.utils.embed import create_embed


class Levels(Cog):
    """Ranking system for the bot."""

    __slots__ = ("bot", "cooldown", "mapping")

    def __init__(self, bot: IBot) -> None:
        self.bot = bot
        # Users can only gain experience once every minute. This is
        # because we don't want users to spam messages to gain
        # experience.
        self.cooldown = CooldownMapping.from_cooldown(1, 60, BucketType.user)

    def get_level_exp(self, level: int) -> int:
        """Get the experience required to reach the given level. The
        formula used to calculate the experience required to reach a
        level is:

        .. code-block:: python

            5 * (level**2) + (50 * level) + 100

        Parameters
        ----------
        level: :class:`int`
            The level to get the experience required to reach it.

        Returns
        -------
        :class:`int`
            The experience required to reach the given level.
        """
        return 5 * (level**2) + (50 * level) + 100

    def get_level_from_exp(self, exp: int) -> int:
        """Get the level from the given experience.

        Parameters
        ----------
        exp: :class:`int`
            The experience to get the level from.

        Returns
        -------
        :class:`int`
            The level from the given experience.
        """
        level = 0

        while exp >= self.get_level_exp(level):
            exp -= self.get_level_exp(level)
            level += 1

        return level

    async def insert_user(self, user_id: int) -> None:
        """Inserts a user into the database with zero experience. This
        should only be used when the user sends a message and doesn't
        exist in the database.

        Parameters
        ----------
        user_id: :class:`int`
            The ID of the user to insert into the database.
        """
        async with self.bot.engine.begin() as conn:
            stmt = insert(LevelUser).values(user_id=user_id)
            await conn.execute(stmt)

    async def get_experience(
        self,
        user_id: int,
        *,
        insert: bool = False,
    ) -> int:
        """Gets the experience of a user. If the user doesn't exist in
        the database, then zero is returned. If the ``insert`` parameter
        is set to ``True``, then the user will be inserted into the
        database if they don't exist.

        Parameters
        ----------
        user_id: :class:`int`
            The ID of the user to get the experience of.
        insert: :class:`bool`
            Whether to insert the user into the database if they don't
            exist. Defaults to ``False``.

        Returns
        -------
        :class:`int`
            The experience of the user, or zero if the user doesn't
            exist in the database.
        """
        async with self.bot.engine.begin() as conn:
            stmt = select(LevelUser).where(LevelUser.user_id == user_id)
            result = (await conn.execute(stmt)).fetchone()

        if result is None and insert:
            await self.insert_user(user_id)

        return result.exp if result is not None else 0

    async def add_experience(self, user_id: int, to_add: int) -> int:
        """Adds experience to a user and returns the new experience. If
        the user doesn't exist in the database, then zero is returned.

        Parameters
        ----------
        user_id: :class:`int`
            The ID of the user to add experience to.
        to_add: :class:`int`
            The amount of experience to add.

        Returns
        -------
        :class:`int`
            The new experience of the user, or zero if the user doesn't
            exist in the database.
        """
        async with self.bot.engine.begin() as conn:
            stmt = (
                update(LevelUser)
                .where(LevelUser.user_id == user_id)
                .values(exp=LevelUser.exp + to_add)
                .returning(LevelUser.exp)
            )
            result = (await conn.execute(stmt)).fetchone()

        return result.exp if result is not None else 0

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        get_role = self.bot.guild.get_role
        value = {k: get_role(v) for k, v in LEVELS_MAPPING.items()}

        # A mapping of levels to roles. This is used to give users roles
        # when they reach a certain level
        self.mapping = cast(Dict[int, Role], value)

    @commands.Cog.listener()
    async def on_regular_message(self, message: Message) -> None:
        author = cast(Member, message.author)
        channel = cast(TextChannel, message.channel)

        # If we are in development mode, only allow messages in the test
        # channel to count towards experience.
        if self.bot.env == "development" and channel.id != TEST_CHANNEL_ID:
            return

        current_exp = await self.get_experience(author.id, insert=True)
        current_level = self.get_level_from_exp(current_exp)

        bucket = self.cooldown.get_bucket(message)
        retry_after = bucket.update_rate_limit() if bucket else None

        if retry_after is not None:
            return

        new_exp = await self.add_experience(author.id, randint(15, 25))
        new_level = self.get_level_from_exp(new_exp)

        # If the new level is different from the current level, then
        # the user has leveled up, so we reply to the message with an
        # embed to notify the user. If the new level is in the level
        # mapping, then we remove all the roles in the mapping from the
        # user (so that the user only has one level role at a time) and
        # add the new level role to the user.
        if new_level != current_level:
            contents = [
                f"Parabéns, {author.mention}! Você subiu para o "
                f"**nível {new_level}**!",
            ]

            if new_level in self.mapping:
                role = self.mapping[new_level]

                # Add a message to the contents to notify the user which
                # role they received when they leveled up.
                contents.append(
                    f"Você recebeu o cargo {role.mention} ao passar "
                    f"para esse nível."
                )

                await author.remove_roles(*self.mapping.values())
                await author.add_roles(role)

            embed = create_embed("\n".join(contents), author=author)
            await message.reply(embed=embed, mention_author=False)


async def setup(bot: IBot) -> None:
    await bot.add_cog(Levels(bot))
