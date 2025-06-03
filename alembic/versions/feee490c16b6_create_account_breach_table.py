"""Create account_breach table

Revision ID: feee490c16b6
Revises: 75b847bb7631
Create Date: 2025-06-03 14:57:02.767037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'feee490c16b6'
down_revision: Union[str, None] = '75b847bb7631'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'account_breach_test',
        sa.Column('account_id', sa.INTEGER),
        sa.Column('breach_id', sa.INTEGER),
        sa.Column('is_alerted', sa.BOOLEAN, nullable=False, default=False),
        sa.ForeignKeyConstraint(['account_id'], ['account_test.id'], name='account_breach_account_id_fkey', ondelete='CASCADE', onupdate='CASCADE'),
        sa.ForeignKeyConstraint(['breach_id'], ['breach_test.id'], name='account_breach_breach_id_fkey', ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('account_id', 'breach_id', name='account_breach_test_pkey'),
    )
    op.create_index('ix_account_breach_test_account_id', 'account_breach_test', ['account_id'], unique=False)
    op.create_index('ix_account_breach_test_breach_id', 'account_breach_test', ['breach_id'], unique=False)



def downgrade() -> None:
    op.drop_index('ix_account_breach_test_account_id', table_name='account_breach_test')
    op.drop_index('ix_account_breach_test_breach_id', table_name='account_breach_test')
    op.drop_table('account_breach_test')
