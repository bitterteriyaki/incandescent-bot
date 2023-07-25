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
from typing import Dict, Optional, cast

from discord import Member, Message, Role, TextChannel
from discord.ext.commands import (  # type: ignore
    Author,
    BucketType,
    Cog,
    CooldownMapping,
    Greedy,
    hybrid_group,
    is_owner,
)
from humanize import intcomma
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert  # type: ignore

from bot.core import IBot
from bot.utils.constants import LEVELS_MAPPING, TEST_CHANNEL_ID
from bot.utils.context import IContext
from bot.utils.database import LevelUser
from bot.utils.embed import create_embed
from bot.utils.formats import human_join


class Levels(Cog, name="Ranking"):
    """Ranking system for the bot."""

    emote = "<:Gang_mitinho:1115116658072223754>"

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
        the user doesn't exist in the database, then they will be
        inserted with the given amount of experience.

        Parameters
        ----------
        user_id: :class:`int`
            The ID of the user to add experience to.
        to_add: :class:`int`
            The amount of experience to add.

        Returns
        -------
        :class:`int`
            The new experience of the user.
        """
        async with self.bot.engine.begin() as conn:
            stmt = (
                insert(LevelUser)  # type: ignore
                .values(user_id=user_id, exp=to_add)
                .on_conflict_do_update(
                    index_elements=[LevelUser.user_id],
                    set_=dict(exp=LevelUser.exp + to_add),
                )
                .returning(LevelUser.exp)
            )
            result = (await conn.execute(stmt)).fetchone()

        return result.exp if result is not None else to_add

    async def bulk_add_experience(self, *user_ids: int, to_add: int) -> None:
        """Adds experience to multiple users. This is more efficient
        than calling :meth:`add_experience` multiple times as it only
        makes one query.

        Parameters
        ----------
        *user_ids: :class:`int`
            The IDs of the users to add experience to.
        to_add: :class:`int`
            The amount of experience to add.
        """
        async with self.bot.engine.begin() as conn:
            for user_id in user_ids:
                stmt = (
                    insert(LevelUser)  # type: ignore
                    .values(user_id=user_id, exp=to_add)
                    .on_conflict_do_update(
                        index_elements=[LevelUser.user_id],
                        set_=dict(exp=LevelUser.exp + to_add),
                    )
                )
                await conn.execute(stmt)

    async def bulk_set_experience(self, *user_ids: int, to_set: int) -> None:
        """Sets the experience of multiple users.

        Parameters
        ----------
        *user_ids: :class:`int`
            The IDs of the users to set the experience of.
        exp: :class:`int`
            The amount of experience to set.
        """
        async with self.bot.engine.begin() as conn:
            for user_id in user_ids:
                stmt = (
                    insert(LevelUser)  # type: ignore
                    .values(user_id=user_id, exp=to_set)
                    .on_conflict_do_update(
                        index_elements=[LevelUser.user_id],
                        set_=dict(exp=to_set),
                    )
                )
                await conn.execute(stmt)

    def draw_experience_bar(self, exp: int, *, width: int = 20) -> str:
        """Draws an experience bar for the given experience.

        Parameters
        ----------
        exp: :class:`int`
            The experience to draw the bar for.
        width: :class:`int`
            The width of the bar. Defaults to ``20``.

        Returns
        -------
        :class:`str`
            The experience bar for the given experience.
        """
        level = self.get_level_from_exp(exp)
        needed_exp = self.get_level_exp(level)

        exp -= sum(self.get_level_exp(i) for i in range(level))
        amount = round((exp / needed_exp) * 100)

        filled = "█" * round(width * (amount / 100))
        empty = "·" * (width - len(filled))

        return f"`[{filled}{empty}]`"

    # Listeners

    @Cog.listener()
    async def on_ready(self) -> None:
        get_role = self.bot.guild.get_role
        value = {k: get_role(v) for k, v in LEVELS_MAPPING.items()}

        # A mapping of levels to roles. This is used to give users roles
        # when they reach a certain level
        self.mapping = cast(Dict[int, Role], value)

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        # If a member leaves the server, then we delete their entry in
        # the database so that they don't take up space.
        async with self.bot.engine.begin() as conn:
            stmt = delete(LevelUser).where(LevelUser.user_id == member.id)
            await conn.execute(stmt)

    @Cog.listener()
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
                f"**nível {intcomma(new_level)}**!",
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

    # Commands

    @hybrid_group(fallback="info", usage="[membro]")
    async def exp(self, ctx: IContext, member: Member = Author) -> None:
        """Informações sobre a experiência do usuário."""
        exp = await self.get_experience(member.id)
        level = self.get_level_from_exp(exp)

        contents = [
            f"**Nível:** {intcomma(level)}",
            f"**Experiência:** {intcomma(exp)}",
            self.draw_experience_bar(exp),
        ]

        embed = create_embed("\n".join(contents), author=ctx.author)

        embed.title = f"Experiência de {member}"
        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.reply(embed=embed)

    @exp.command(name="add", usage="<usuários...> <quantidade>")
    @is_owner()
    async def exp_add(
        self,
        ctx: IContext,
        members: Greedy[Member],
        amount: int,
    ) -> Optional[Message]:
        """Adiciona experiência a um ou mais usuários."""
        if not members:
            return await ctx.reply(
                "Você precisa mencionar pelo menos um usuário."
            )

        if amount <= 0:
            return await ctx.reply(
                "A quantidade de experiência deve ser maior que zero."
            )

        users_ids = [member.id for member in members]
        await self.bulk_add_experience(*users_ids, to_add=amount)

        mentions = human_join([member.mention for member in members])
        exp = intcomma(amount)

        await ctx.reply(f"Adicionado `{exp}` de experiência para {mentions}.")

    @exp.command(name="remove", usage="<usuários...> <quantidade>")
    @is_owner()
    async def exp_remove(
        self,
        ctx: IContext,
        members: Greedy[Member],
        amount: int,
    ) -> Optional[Message]:
        """Remove experiência de um ou mais usuários."""
        if not members:
            return await ctx.reply(
                "Você precisa mencionar pelo menos um usuário."
            )

        if amount <= 0:
            return await ctx.reply(
                "A quantidade de experiência deve ser maior que zero."
            )

        users_ids = [member.id for member in members]
        await self.bulk_add_experience(*users_ids, to_add=-amount)

        mentions = human_join([member.mention for member in members])
        exp = intcomma(amount)

        await ctx.reply(f"Removido `{exp}` de experiência de {mentions}.")

    @exp.command(name="set", usage="<usuários...> <quantidade>")
    @is_owner()
    async def exp_set(
        self,
        ctx: IContext,
        members: Greedy[Member],
        amount: int,
    ) -> Optional[Message]:
        """Define a experiência de um ou mais usuários."""
        if not members:
            return await ctx.reply(
                "Você precisa mencionar pelo menos um usuário."
            )

        if amount <= 0:
            return await ctx.reply(
                "A quantidade de experiência deve ser maior que zero."
            )

        users_ids = [member.id for member in members]
        await self.bulk_set_experience(*users_ids, to_set=amount)

        mentions = human_join([member.mention for member in members])
        exp = intcomma(amount)

        await ctx.reply(f"Definido `{exp}` de experiência para {mentions}.")


async def setup(bot: IBot) -> None:
    await bot.add_cog(Levels(bot))
