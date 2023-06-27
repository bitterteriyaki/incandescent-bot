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

from os import environ

from sqlalchemy import BigInteger, Column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

DB_USER = environ["POSTGRES_USER"]
DB_PASS = environ["POSTGRES_PASSWORD"]
DB_HOST = environ["POSTGRES_HOST"]
DB_PORT = environ["POSTGRES_PORT"]
DB_NAME = environ["POSTGRES_DB"]

DB_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models."""


class LevelUser(Base):
    """Represents a user's level."""

    __tablename__ = "levels"

    user_id = Column(BigInteger, primary_key=True)
    exp = Column(BigInteger, default=0)
