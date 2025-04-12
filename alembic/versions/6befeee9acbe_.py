"""empty message

Revision ID: 6befeee9acbe
Revises: 612ec91e755b
Create Date: 2025-04-12 17:17:49.826071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6befeee9acbe'
down_revision: Union[str, None] = '612ec91e755b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
