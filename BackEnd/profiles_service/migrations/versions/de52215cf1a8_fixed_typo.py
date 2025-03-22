"""fixed typo

Revision ID: de52215cf1a8
Revises: f00f18d00977
Create Date: 2025-03-18 15:21:50.524327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de52215cf1a8'
down_revision: Union[str, None] = 'f00f18d00977'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.rename_table('starup_category', 'startup_category')
    op.rename_table('starup_profile_category', 'startup_profile_category')

def downgrade():
    op.rename_table('startup_category', 'starup_category')
    op.rename_table('startup_profile_category', 'starup_profile_category')
