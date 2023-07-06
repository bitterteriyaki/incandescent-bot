"""create messages table

Revision ID: cec1ef5dab8b
Revises: 57ec8d1ee415
Create Date: 2023-07-06 14:00:30.118177
"""

from alembic.op import create_table, drop_table
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    PrimaryKeyConstraint,
    String,
)

revision = "cec1ef5dab8b"
down_revision = "57ec8d1ee415"
branch_labels = None
depends_on = None


def upgrade() -> None:
    create_table(
        "messages",
        Column("message_id", BigInteger(), nullable=False),
        Column("author_id", BigInteger(), nullable=True),
        Column("channel_id", BigInteger(), nullable=True),
        Column("content", String(), nullable=True),
        Column("created_at", DateTime(), nullable=True),
        PrimaryKeyConstraint("message_id"),
    )


def downgrade() -> None:
    drop_table("messages")
