"""Initial schema: the five tables of the park.

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Declaration order is fare priority, and Postgres sorts an enum that way.
ticket_role = postgresql.ENUM(
    "super_sayan", "sayan", "normal", name="ticket_role", create_type=False
)


def upgrade() -> None:
    ticket_role.create(op.get_bind(), checkfirst=True)

    # "user" is a Postgres reserved word: it lives in quotes.
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.String(length=128), nullable=False),
        sa.Column("is_staff", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_user"),
        sa.UniqueConstraint("username", name="uq_user_username"),
    )

    op.create_table(
        "ticket",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("numero", sa.String(length=32), nullable=False),
        sa.Column("role", ticket_role, server_default="normal", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name="fk_ticket_user_id_user", ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_ticket"),
        sa.UniqueConstraint("numero", name="uq_ticket_numero"),
    )
    op.create_index("ix_ticket_user_id", "ticket", ["user_id"])

    op.create_table(
        "attraction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("max_people", sa.Integer(), nullable=False),
        sa.Column(
            "avg_duration",
            sa.Integer(),
            server_default=sa.text("120"),
            nullable=False,
            comment="one ride, in seconds",
        ),
        sa.Column(
            "people_inside",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
            comment="counter kept in step with attraction_visit, not a count",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_attraction"),
    )

    # The queue of the moment: one ticket holds at most one place per attraction.
    op.create_table(
        "queue_entry",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("attraction_id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("joined_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("is_ready", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("ready_at", sa.DateTime(), nullable=True),
        sa.Column(
            "max_seconds_allowing_ready",
            sa.Integer(),
            server_default=sa.text("300"),
            nullable=False,
            comment="grace period in seconds before the ready state expires",
        ),
        sa.ForeignKeyConstraint(
            ["attraction_id"],
            ["attraction.id"],
            name="fk_queue_entry_attraction_id_attraction",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["ticket_id"], ["ticket.id"], name="fk_queue_entry_ticket_id_ticket", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_queue_entry"),
        sa.UniqueConstraint(
            "attraction_id", "ticket_id", name="uq_queue_entry_ticket_per_attraction"
        ),
        comment="Virtual queue: one row per ticket waiting on an attraction.",
    )
    op.create_index("ix_queue_entry_attraction_id", "queue_entry", ["attraction_id"])
    op.create_index("ix_queue_entry_ticket_id", "queue_entry", ["ticket_id"])

    # Current presence: written on entry, deleted on exit.
    op.create_table(
        "attraction_visit",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("attraction_id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("entered_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["attraction_id"],
            ["attraction.id"],
            name="fk_attraction_visit_attraction_id_attraction",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["ticket.id"],
            name="fk_attraction_visit_ticket_id_ticket",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_attraction_visit"),
        sa.UniqueConstraint("attraction_id", "ticket_id", name="uq_visit_ticket_per_attraction"),
        comment="Current presence: one row per visitor inside the attraction right now.",
    )
    op.create_index("ix_attraction_visit_attraction_id", "attraction_visit", ["attraction_id"])
    op.create_index("ix_attraction_visit_ticket_id", "attraction_visit", ["ticket_id"])


def downgrade() -> None:
    op.drop_table("attraction_visit")
    op.drop_table("queue_entry")
    op.drop_table("attraction")
    op.drop_table("ticket")
    op.drop_table("user")
    ticket_role.drop(op.get_bind(), checkfirst=True)
