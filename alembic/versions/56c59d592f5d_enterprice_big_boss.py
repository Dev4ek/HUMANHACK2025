"""enterprice_big_boss

Revision ID: 56c59d592f5d
Revises: 1aa888a0d7ac
Create Date: 2025-04-13 05:35:47.855854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56c59d592f5d'
down_revision: Union[str, None] = '1aa888a0d7ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('enterprises', sa.Column('boss_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'enterprises', 'employees', ['boss_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'enterprises', type_='foreignkey')
    op.drop_column('enterprises', 'boss_id')
    # ### end Alembic commands ###
