"""create levels table

Revision ID: 57ec8d1ee415
Revises:
Create Date: 2023-06-26 22:22:02.215823
"""

from alembic.op import create_table, drop_table  # type: ignore
from sqlalchemy import BigInteger, Column, PrimaryKeyConstraint

revision = "57ec8d1ee415"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    create_table(
        "levels",
        Column("user_id", BigInteger(), nullable=False),
        Column("exp", BigInteger(), nullable=True),
        PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    drop_table("levels")
