"""create user table

Revision ID: 5bf0925c7f38
Revises: d9dc47b036af
Create Date: 2026-08-14 13:59:20.208446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5bf0925c7f38'
down_revision: Union[str, Sequence[str], None] = 'd9dc47b036af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('user_tb',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('telegram_chat_id', sa.String(), nullable=True),
    sa.Column('alert_email', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_tb')
