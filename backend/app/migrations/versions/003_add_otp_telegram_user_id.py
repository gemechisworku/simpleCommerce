"""Add telegram_user_id to otp_codes to link phone+Telegram on verify

Revision ID: 003_otp_telegram_user_id
Revises: 002_otp_delivery_token
Create Date: 2025-03-13

"""
from alembic import op
import sqlalchemy as sa

revision = "003_otp_telegram_user_id"
down_revision = "002_otp_delivery_token"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "otp_codes",
        sa.Column("telegram_user_id", sa.String(100), nullable=True),
    )
    op.create_index(
        op.f("ix_otp_codes_telegram_user_id"),
        "otp_codes",
        ["telegram_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_otp_codes_telegram_user_id"), table_name="otp_codes")
    op.drop_column("otp_codes", "telegram_user_id")
