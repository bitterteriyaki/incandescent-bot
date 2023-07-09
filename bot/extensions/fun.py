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

from typing import List, cast

from aiocron import crontab  # type: ignore
from discord import Member, Role, TextChannel
from discord.ext.commands import Cog  # type: ignore
from discord.utils import cached_property
from humanize import intcomma
from sqlalchemy import func, select, text

from bot.core import IBot
from bot.utils.constants import CHATTY_CHANNEL_ID, CHATTY_ROLE_ID
from bot.utils.database import DiscordMessage
from bot.utils.embed import create_embed


class Fun(Cog):
    """Fun related commands and events."""

    def __init__(self, bot: IBot) -> None:
        self.bot = bot
        self.task = crontab(  # type: ignore
            "0 15 * * 1",
            func=self.chatty_event,
            start=False,
        )

        if bot.env == "production":
            self.task.start()  # type: ignore

    @cached_property
    def chatty_channel(self) -> TextChannel:
        return cast(TextChannel, self.bot.guild.get_channel(CHATTY_CHANNEL_ID))

    @cached_property
    def chatty_role(self) -> Role:
        return cast(Role, self.bot.guild.get_role(CHATTY_ROLE_ID))

    async def chatty_event(self) -> None:
        members: List[str] = []

        async with self.bot.engine.begin() as conn:
            count = func.count().label("count")
            interval = text("CURRENT_TIMESTAMP - INTERVAL '7 DAYS'")

            stmt = (
                select(DiscordMessage.author_id, count)
                .where(DiscordMessage.created_at > interval)
                .group_by(DiscordMessage.author_id)
                .order_by(count.desc())
                .limit(10)
            )
            result = (await conn.execute(stmt)).all()

        for idx, row in enumerate(result, start=1):
            member = cast(Member, self.bot.guild.get_member(row[0]))
            total = intcomma(row[1])

            content = f"**{idx}.** {member.mention} ({total} mensagens)"
            members.append(content)

        member_id, total = result[0]
        chatty = cast(Member, self.bot.guild.get_member(member_id))

        content = (
            f"{chatty.mention} foi o mais tagarela da semana com um total de "
            f"**{intcomma(total)} mensagens**, parabéns! Você receberá o "
            f"cargo {self.chatty_role.mention} por uma semana."
        )
        ranking = "\n".join(members)

        for member in self.chatty_role.members:
            # They don't deserve the role anymore...
            await member.remove_roles(self.chatty_role)

        await chatty.add_roles(self.chatty_role)

        embed = create_embed(f"{content}\n\n{ranking}")
        embed.title = "\U0001f4e2 Ranking de mensagens semanal"

        await self.chatty_channel.send(embed=embed)


async def setup(bot: IBot) -> None:
    await bot.add_cog(Fun(bot))
