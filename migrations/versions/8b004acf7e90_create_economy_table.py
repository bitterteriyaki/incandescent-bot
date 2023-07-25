"""create economy table

Revision ID: 8b004acf7e90
Revises: 3627fa04dcf8
Create Date: 2023-07-24 22:58:49.286859
"""

from alembic.op import create_table, drop_table  # type: ignore
from sqlalchemy import BigInteger, Column, PrimaryKeyConstraint

revision = "8b004acf7e90"
down_revision = "3627fa04dcf8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    create_table(
        "economy",
        Column("user_id", BigInteger(), nullable=False),
        Column("balance", BigInteger(), nullable=False),
        PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    drop_table("economy")
