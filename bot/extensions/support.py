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

from typing import Any, List, Mapping, Optional, cast

from discord import Member
from discord.ext.commands import Cog, Command, HelpCommand  # type: ignore

from bot.core import IBot
from bot.utils.embed import create_embed


class IHelpCommand(HelpCommand):
    """Custom help command."""

    def __init__(self) -> None:
        super().__init__()
        self.command_attrs["help"] = "Mostra essa mensagem."
        self.command_attrs["usage"] = "[comando]"

    async def send_bot_help(
        self, mapping: Mapping[Optional[Cog], List[Command[Any, ..., Any]]]
    ) -> None:
        ctx = self.context
        author = cast(Member, ctx.author)

        cmd = f"{ctx.clean_prefix}{ctx.invoked_with}"
        content = f"Use `{cmd} [comando]` para mais informações de um comando."

        embed = create_embed(content, author=author)

        for cog, commands in mapping.items():
            filtered_commands = await self.filter_commands(commands, sort=True)

            if cog is None or not commands:
                continue

            cog = f"{cog.emote} {cog.qualified_name}"
            commands = [f"`{command.name}`" for command in filtered_commands]
            embed.add_field(name=cog, value=", ".join(commands), inline=False)

        await ctx.reply(embed=embed)

    async def send_command_help(self, command: Command[Any, ..., Any]) -> None:
        ctx = self.context
        author = cast(Member, ctx.author)

        embed = create_embed(command.help, author=author)

        #
        # Usage
        #
        prefix = ctx.clean_prefix
        emote = "<:Gato_nerd:1098057823910363337>"

        usage = f"{prefix}{command.qualified_name}"
        embed.title = f"{emote} `{usage} {command.usage}`"

        #
        # Aliases
        #
        if command.aliases:
            aliases = ", ".join(f"`{alias}`" for alias in command.aliases)
        else:
            aliases = "Este comando não possui pseudônimos."

        name = "\U0001f38f Pseudônimos"
        embed.add_field(name=name, value=aliases, inline=False)

        await ctx.reply(embed=embed)


class Support(Cog, name="Suporte"):
    """Support system related commands."""

    emote = "<:Gato_nerd:1098057823910363337>"

    def __init__(self, bot: IBot) -> None:
        self.bot = bot
        self.original_help_command = bot.help_command

        bot.help_command = IHelpCommand()
        bot.help_command.cog = self

    async def cog_unload(self) -> None:
        self.bot.help_command = self.original_help_command


async def setup(bot: IBot) -> None:
    await bot.add_cog(Support(bot))
