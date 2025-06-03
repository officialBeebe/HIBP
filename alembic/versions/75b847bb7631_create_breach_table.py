"""Create breach table

Revision ID: 75b847bb7631
Revises: ff651e8da2e9
Create Date: 2025-06-03 14:56:45.422146

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75b847bb7631'
down_revision: Union[str, None] = 'ff651e8da2e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'breach_test',
        sa.Column('id', sa.INTEGER, primary_key=True, autoincrement=True),
        sa.Column('name', sa.TEXT, unique=True, nullable=False),
        sa.Column('title', sa.TEXT, nullable=True),
        sa.Column('domain', sa.TEXT, nullable=True),
        sa.Column('breach_date', sa.DATE, nullable=True),
        sa.Column('added_date', sa.DATE, nullable=True),
        sa.Column('modified_date', sa.DATE, nullable=True),
        sa.Column('pwn_count', sa.BIGINT, nullable=True),
        sa.Column('description', sa.TEXT, nullable=True),
        sa.Column('logo_path', sa.TEXT, nullable=True),
        sa.Column('data_classes', sa.ARRAY(sa.TEXT), nullable=True),
        sa.Column('is_verified', sa.BOOLEAN, nullable=True),
        sa.Column('is_fabricated', sa.BOOLEAN, nullable=True),
        sa.Column('is_sensitive', sa.BOOLEAN, nullable=True),
        sa.Column('is_retired', sa.BOOLEAN, nullable=True),
        sa.Column('is_spam_list', sa.BOOLEAN, nullable=True),
        sa.Column('is_malware', sa.BOOLEAN, nullable=True),
        sa.Column('is_subscription_free', sa.BOOLEAN, nullable=True),
        sa.Column('is_stealer_log', sa.BOOLEAN, nullable=True),
    )
    op.create_index('ix_breach_test_id', 'breach_test', ['id'])
    op.create_index('ix_breach_test_name', 'breach_test', ['name'])



def downgrade() -> None:
    op.drop_index('ix_breach_test_id', table_name='breach_test')
    op.drop_index('ix_breach_test_name', table_name='breach_test')
    op.drop_table('breach_test')
