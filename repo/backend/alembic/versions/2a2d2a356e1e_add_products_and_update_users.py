"""add products table and update users table

Revision ID: 2a2d2a356e1e
Revises: d1e89e0d8b51
Create Date: 2025-06-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a2d2a356e1e'
down_revision: Union[str, Sequence[str], None] = 'd1e89e0d8b51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('stock_quantity', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index(op.f('ix_products_id'), 'id', unique=False),
        schema="dev"
    )

    with op.batch_alter_table('users', schema="dev") as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
        batch_op.alter_column('password', new_column_name='password_hash', existing_type=sa.String(), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('users', schema="dev") as batch_op:
        batch_op.alter_column('password_hash', new_column_name='password', existing_type=sa.String())
        batch_op.drop_column('created_at')

    op.drop_table('products', schema="dev") 