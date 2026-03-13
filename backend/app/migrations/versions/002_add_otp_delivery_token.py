"""Add delivery_token to otp_codes for Telegram OTP link flow

Revision ID: 002_otp_delivery_token
Revises: 931e6bf7cc20
Create Date: 2025-03-13

"""
from alembic import op
import sqlalchemy as sa

revision = "002_otp_delivery_token"
down_revision = "931e6bf7cc20"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "otp_codes",
        sa.Column("delivery_token", sa.String(64), nullable=True),
    )
    op.create_index(
        op.f("ix_otp_codes_delivery_token"),
        "otp_codes",
        ["delivery_token"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_otp_codes_delivery_token"), table_name="otp_codes")
    op.drop_column("otp_codes", "delivery_token")
