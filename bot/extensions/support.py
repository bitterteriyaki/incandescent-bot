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

from typing import Any, List, Mapping, Optional

from discord.ext.commands import (  # type: ignore
    Cog,
    Command,
    Group,
    HelpCommand,
)

from bot.core import IBot
from bot.utils.constants import (
    GATO_NERD_EMOTE,
    PSEUDONYMS_EMOTE,
    SUBCOMMANDS_EMOTE,
)
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

        usage = self.command_attrs["usage"]
        cmd = f"{ctx.clean_prefix}{ctx.invoked_with} {usage}"

        content = f"Use `{cmd}` para mais informações de um comando."
        embed = create_embed(content, author=ctx.author)

        for cog, commands in mapping.items():
            filtered_commands = await self.filter_commands(commands, sort=True)

            if cog is None or not commands:
                continue

            cog = f"{cog.emote} {cog.qualified_name}"
            commands = [f"`{command.name}`" for command in filtered_commands]
            embed.add_field(name=cog, value=", ".join(commands), inline=False)

        await ctx.reply(embed=embed)

    async def send_group_help(self, group: Group[Any, ..., Any]) -> None:
        ctx = self.context

        embed = create_embed(group.help, author=ctx.author)
        prefix = ctx.clean_prefix

        if group.usage is None:
            usage = f"{prefix}{group.qualified_name}"
        else:
            usage = f"{prefix}{group.qualified_name} {group.usage}"

        embed.title = f"{GATO_NERD_EMOTE} `{usage}`"

        if group.aliases:
            aliases = ", ".join(f"`{alias}`" for alias in group.aliases)
        else:
            aliases = "Este comando não possui pseudônimos."

        name = f"{PSEUDONYMS_EMOTE} Pseudônimos"
        embed.add_field(name=name, value=aliases, inline=False)

        subcommands = [f"`{command.name}`" for command in group.commands]
        name = f"{SUBCOMMANDS_EMOTE} Subcomandos"

        embed.add_field(name=name, value=", ".join(subcommands), inline=False)

        await ctx.reply(embed=embed)

    async def send_command_help(self, command: Command[Any, ..., Any]) -> None:
        ctx = self.context

        embed = create_embed(command.help, author=ctx.author)
        prefix = ctx.clean_prefix

        if command.usage is None:
            usage = f"{prefix}{command.qualified_name}"
        else:
            usage = f"{prefix}{command.qualified_name} {command.usage}"

        embed.title = f"{GATO_NERD_EMOTE} `{usage}`"

        if command.aliases:
            aliases = ", ".join(f"`{alias}`" for alias in command.aliases)
        else:
            aliases = "Este comando não possui pseudônimos."

        name = f"{PSEUDONYMS_EMOTE} Pseudônimos"
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
