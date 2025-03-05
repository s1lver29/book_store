"""Add seller database

Revision ID: 329c14804d57
Revises: e6388b5c5964
Create Date: 2025-03-05 19:41:29.099207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '329c14804d57'
down_revision: Union[str, None] = 'e6388b5c5964'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sellers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('e_mail', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('e_mail')
    )
    op.add_column('books', sa.Column('seller_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'books', 'sellers', ['seller_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'books', type_='foreignkey')
    op.drop_column('books', 'seller_id')
    op.drop_table('sellers')
    # ### end Alembic commands ###
