"""add phone column to user

Revision ID: b5065c533296
Revises: 
Create Date: 2023-11-10 14:34:18.665916

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5065c533296'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'user',
        sa.Column(
            'phone',
            sa.String(),
            nullable=False,
            server_default='+910000000000'
        )
    )


def downgrade() -> None:
    op.drop_column('user','phone')
