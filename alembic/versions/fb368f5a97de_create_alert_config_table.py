"""create alert config table

Revision ID: fb368f5a97de
Revises: d595069ae60e
Create Date: 2026-08-14 13:59:21.220738

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb368f5a97de'
down_revision: Union[str, Sequence[str], None] = 'd595069ae60e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('alert_config_tb',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('variable', sa.String(), nullable=False),
    sa.Column('condition', sa.String(), nullable=False),
    sa.Column('threshold', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user_tb.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('alert_config_tb')
