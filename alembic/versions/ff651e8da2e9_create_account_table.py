"""create account table

Revision ID: ff651e8da2e9
Revises: 
Create Date: 2025-06-03 14:01:52.496799

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff651e8da2e9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'account_test',
        sa.Column('id', sa.INTEGER, primary_key=True, autoincrement=True),
        sa.Column('email', sa.TEXT, nullable=False, unique=True),
        sa.Column('date_added', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_account_test_email', 'account_test', ['email'])



def downgrade() -> None:
    op.drop_index('ix_account_test_email', table_name='account_test')
    op.drop_table('account_test')

