"""empty message

Revision ID: 0e0c72f3539a
Revises: 58b83a66082a
Create Date: 2025-03-13 07:39:41.145904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0e0c72f3539a'
down_revision: Union[str, None] = '58b83a66082a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.rename_table('profiles', 'startup_profiles')

def downgrade():
    op.rename_table('startup_profiles', 'profiles')
