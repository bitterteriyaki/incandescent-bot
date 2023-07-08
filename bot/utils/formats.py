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

from typing import Sequence


def human_join(
    sequence: Sequence[str],
    *,
    delimiter: str = ", ",
    final: str = "e",
) -> str:
    """Humanize a sequence of strings. This is useful for lists of
    users, channels, etc.

    Parameters
    ----------
    sequence: Sequence[:class:`str`]
        The sequence of strings to humanize.
    delimiter: :class:`str`
        The delimiter to use between each string.
    final: :class:`str`
        The final delimiter to use between the penultimate and last
        string.

    Returns
    -------
    :class:`str`
        The humanized string.
    """
    size = len(sequence)

    if size == 0:
        return ""

    if size == 1:
        return sequence[0]

    if size == 2:
        return f"{sequence[0]} {final} {sequence[1]}"

    return delimiter.join(sequence[:-1]) + f" {final} {sequence[-1]}"
