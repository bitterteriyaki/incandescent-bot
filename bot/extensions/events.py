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

from io import BytesIO
from typing import cast

from discord import File, Member, Message, TextChannel
from discord.ext.commands import Cog  # type: ignore
from discord.utils import cached_property
from PIL import Image, ImageDraw
from sqlalchemy import insert

from bot.core import IBot
from bot.utils.constants import GENERAL_CHANNEL_ID, WELCOME_EMOTE
from bot.utils.database import DiscordMessage
from bot.utils.embed import create_embed


class Events(Cog):
    """Handles many Discord events."""

    def __init__(self, bot: IBot) -> None:
        self.bot = bot

        with open("bot/assets/welcome.png", "rb") as f:
            self.welcome_bytes = BytesIO(f.read())

        self.size = (500, 500)
        self.coords = (208, 257)

        self.mask = Image.new("L", self.size, 0)
        self.background = Image.new("RGBA", self.size, 0)

        draw = ImageDraw.Draw(self.mask)
        draw.ellipse((4, 4, self.size[0] - 4, self.size[1] - 4), fill=255)

    @cached_property
    def general_channel(self) -> TextChannel:
        return cast(
            TextChannel, self.bot.guild.get_channel(GENERAL_CHANNEL_ID)
        )

    @Cog.listener()
    async def on_ready(self) -> None:
        print(f"Logged in as {self.bot.user}.")

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        async with self.bot.engine.begin() as conn:
            stmt = insert(DiscordMessage).values(
                message_id=message.id,
                author_id=message.author.id,
                channel_id=message.channel.id,
                content=message.content,
                created_at=message.created_at.replace(tzinfo=None),
            )
            await conn.execute(stmt)

        self.bot.dispatch("regular_message", message)

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        welcome = Image.open(self.welcome_bytes)
        output = BytesIO()

        async with self.bot.session.get(member.display_avatar.url) as res:
            image_bytes = BytesIO(await res.read())

        avatar = Image.open(image_bytes).resize(self.size)

        rounded = Image.composite(avatar, self.background, self.mask)
        welcome.paste(rounded, box=self.coords, mask=self.mask)

        welcome.save(output, format="PNG")
        output.seek(0)

        content = (
            f"Olá, {member.mention}! Seja bem-vindo(a) ao **Incandescent "
            f"Society**! Esperamos que você se divirta bastante aqui."
        )

        embed = create_embed(content)
        embed.title = f"Seja bem-vindo(a)! {WELCOME_EMOTE}"
        embed.set_image(url="attachment://welcome.png")

        file = File(output, filename="welcome.png")
        await self.general_channel.send(member.mention, file=file, embed=embed)


async def setup(bot: IBot) -> None:
    await bot.add_cog(Events(bot))
