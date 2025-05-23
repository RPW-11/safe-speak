"""add img_url attribute

Revision ID: 44b98cf34b35
Revises: 0bc57844a6ab
Create Date: 2025-05-18 16:35:01.599565

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44b98cf34b35'
down_revision: Union[str, None] = '0bc57844a6ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('User', sa.Column('img_url', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('User', 'img_url')
    # ### end Alembic commands ###
