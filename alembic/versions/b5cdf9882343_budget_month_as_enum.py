"""budget month as enum

Revision ID: b5cdf9882343
Revises: 40a3be6d4c1a
Create Date: 2026-10-09 15:45:57.708966

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5cdf9882343'
down_revision: Union[str, Sequence[str], None] = '40a3be6d4c1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # The year is dropped: an old budget for 2026-10-01 becomes "october".
    # If one category had budgets for the same month in two different years, the unique
    # constraint (category_id, month) makes this fail; merge or remove those rows first.
    op.alter_column('budgets', 'month',
               existing_type=sa.DATE(),
               type_=sa.Enum('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december', name='month', native_enum=False, length=10),
               existing_nullable=False,
               postgresql_using="lower(trim(to_char(month, 'Month')))")


def downgrade() -> None:
    """Downgrade schema."""
    # The original year is lost, so every budget goes back to the year 2000 (e.g. "october" -> 2000-10-01).
    op.alter_column('budgets', 'month',
               existing_type=sa.Enum('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december', name='month', native_enum=False, length=10),
               type_=sa.DATE(),
               existing_nullable=False,
               postgresql_using="to_date('2000 ' || initcap(month) || ' 1', 'YYYY Month DD')")
