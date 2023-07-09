"""set the nullable field to false by default

Revision ID: 3627fa04dcf8
Revises: cec1ef5dab8b
Create Date: 2023-07-09 02:52:44.432950
"""

from alembic.op import alter_column  # type: ignore
from sqlalchemy.dialects.postgresql import BIGINT, TIMESTAMP, VARCHAR

revision = "3627fa04dcf8"
down_revision = "cec1ef5dab8b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    alter_column("levels", "exp", existing_type=BIGINT(), nullable=False)
    alter_column(
        "messages", "author_id", existing_type=BIGINT(), nullable=False
    )
    alter_column(
        "messages", "channel_id", existing_type=BIGINT(), nullable=False
    )
    alter_column(
        "messages", "content", existing_type=VARCHAR(), nullable=False
    )
    alter_column(
        "messages", "created_at", existing_type=TIMESTAMP(), nullable=False
    )


def downgrade() -> None:
    alter_column(
        "messages", "created_at", existing_type=TIMESTAMP(), nullable=True
    )
    alter_column("messages", "content", existing_type=VARCHAR(), nullable=True)
    alter_column(
        "messages", "channel_id", existing_type=BIGINT(), nullable=True
    )
    alter_column(
        "messages", "author_id", existing_type=BIGINT(), nullable=True
    )
    alter_column("levels", "exp", existing_type=BIGINT(), nullable=True)
