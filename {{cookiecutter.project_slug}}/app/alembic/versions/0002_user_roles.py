"""user roles and resource grants

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-08 00:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), server_default="user", nullable=False),
    )
    op.execute("UPDATE users SET role = 'admin' WHERE is_superuser")
    op.drop_column("users", "is_superuser")

    op.create_table(
        "resource_grants",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("resource_id", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "resource_type", "resource_id"),
    )


def downgrade() -> None:
    op.drop_table("resource_grants")

    op.add_column(
        "users",
        sa.Column("is_superuser", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.execute("UPDATE users SET is_superuser = true WHERE role = 'admin'")
    op.drop_column("users", "role")
