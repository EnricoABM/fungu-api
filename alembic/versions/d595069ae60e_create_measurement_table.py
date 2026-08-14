"""create measurement table

Revision ID: d595069ae60e
Revises: 5bf0925c7f38
Create Date: 2026-08-14 13:59:20.706194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd595069ae60e'
down_revision: Union[str, Sequence[str], None] = '5bf0925c7f38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('measurement_tb',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('measured_at', sa.DateTime(), nullable=False),
    sa.Column('variable', sa.String(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('measurement_tb')
