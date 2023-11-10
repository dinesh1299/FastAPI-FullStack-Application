"""Add phone num to user

Revision ID: 434d5eb0dce3
Revises: 
Create Date: 2023-11-10 10:30:57.653307

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '434d5eb0dce3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'user',
        sa.Column('phone',
            sa.Integer(),
            nullable=False,
            server_default='+910000000000'
        ),
    )


def downgrade() -> None:
    pass
