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

from os import walk
from os.path import splitext
from typing import List


def get_extensions(*, path: str = "bot/extensions") -> List[str]:
    """Returns a list of extensions in the given path. Extensions are
    files that end with ``.py``.

    Parameters
    ----------
    path: :class:`str`
        The path to search for extensions in.

    Returns
    -------
    List[:class:`str`]
        A list of extensions in the given path.
    """
    extensions: List[str] = []

    for root, _, files in walk(path):
        for file in files:
            filename, ext = splitext(file)

            if ext != ".py":
                continue

            root = root.replace("/", ".")
            extensions.append(f"{root}.{filename}")

    return extensions
