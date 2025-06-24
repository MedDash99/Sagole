"""Create audit_log table

Revision ID: d1e89e0d8b51
Revises: 5fc9f7387e40
Create Date: 2025-06-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1e89e0d8b51'
down_revision: Union[str, Sequence[str], None] = '5fc9f7387e40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('pending_change_id', sa.Integer(), sa.ForeignKey('pending_changes.id'), nullable=False),
        sa.Column('table_name', sa.String(), nullable=False),
        sa.Column('record_id', sa.String(), nullable=False),
        sa.Column('before_state', sa.JSON(), nullable=True),
        sa.Column('after_state', sa.JSON(), nullable=False),
        sa.Column('approved_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('audit_log') 