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
from typing import cast

from discord import Member
from discord.ext.commands import (  # type: ignore
    Author,
    BucketType,
    Cog,
    cooldown,
    hybrid_command,
)
from humanize import intcomma
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert  # type: ignore

from bot.core import IBot
from bot.utils.constants import INCANDECOIN_EMOTE
from bot.utils.context import IContext
from bot.utils.database import EconomyUser


class Economy(Cog, name="Economia"):
    """Economy system and currency commands."""

    emote = "<:corin:1120221374280114246>"

    def __init__(self, bot: IBot) -> None:
        self.bot = bot

    async def add_coins(self, user_id: int, to_add: int) -> int:
        """Adds the given amount of coins to the given user's balance.
        If the user does not exist in the database, they will be
        inserted with the given amount of coins.

        Parameters
        ----------
        user_id: :class:`int`
            The ID of the user to add coins to.
        to_add: :class:`int`
            The amount of coins to add to the user's balance.

        Returns
        -------
        :class:`int`
            The user's new balance.
        """
        async with self.bot.engine.begin() as conn:
            stmt = (
                insert(EconomyUser)  # type: ignore
                .values(user_id=user_id, balance=to_add)
                .on_conflict_do_update(
                    index_elements=[EconomyUser.user_id],
                    set_=dict(balance=EconomyUser.balance + to_add),
                )
                .returning(EconomyUser.balance)
            )
            result = (await conn.execute(stmt)).fetchone()

        return result.balance if result is not None else to_add

    @hybrid_command()
    @cooldown(1, 86400, BucketType.user)
    async def daily(self, ctx: IContext) -> None:
        """Receba seus incandecoins diários."""
        author = cast(Member, ctx.author)

        interval = (150, 375) if ctx.is_booster() else (100, 150)
        to_add = randint(*interval)

        await self.add_coins(author.id, to_add)
        await ctx.reply(
            f"{author.mention} recebeu **{to_add} {INCANDECOIN_EMOTE}**!"
        )

    @hybrid_command(aliases=["bal"], usage="[membro]")
    async def balance(self, ctx: IContext, *, member: Member = Author) -> None:
        """Veja a sua balança ou a balança de outro membro."""
        async with self.bot.engine.begin() as conn:
            stmt = select(EconomyUser.balance).where(
                EconomyUser.user_id == member.id
            )
            result = (await conn.execute(stmt)).fetchone()

        coins = result.balance if result is not None else 0
        amount = f"{intcomma(coins)} {INCANDECOIN_EMOTE}"

        await ctx.reply(f"{member.mention} tem **{amount}**.")


async def setup(bot: IBot) -> None:
    await bot.add_cog(Economy(bot))
