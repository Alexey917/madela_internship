"""fix timestamp column names

Revision ID: a7cb9b5b4472
Revises: d2a9878b7819
Create Date: 2026-10-19 21:49:38.332170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7cb9b5b4472'
down_revision: Union[str, Sequence[str], None] = 'd2a9878b7819'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('products', 'create_at', new_column_name='created_at')
    op.alter_column('products', 'update_at', new_column_name='updated_at')


def downgrade() -> None:
    op.alter_column('products', 'created_at', new_column_name='create_at')
    op.alter_column('products', 'updated_at', new_column_name='update_at')
