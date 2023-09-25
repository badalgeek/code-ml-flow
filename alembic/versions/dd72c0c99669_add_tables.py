"""Add tables.

Revision ID: dd72c0c99669
Revises: 0bdc5fb2ff19
Create Date: 2023-09-26 01:13:15.266261

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd72c0c99669'
down_revision: Union[str, None] = '0bdc5fb2ff19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('git_commits', sa.Column('metric_file_id', sa.Integer(), nullable=True))
    op.alter_column('git_commits', 'repository_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_foreign_key(None, 'git_commits', 'metric_files', ['metric_file_id'], ['id'])
    op.alter_column('metric_files', 'repository_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_constraint('metric_files_commit_id_fkey', 'metric_files', type_='foreignkey')
    op.drop_column('metric_files', 'commit_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('metric_files', sa.Column('commit_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('metric_files_commit_id_fkey', 'metric_files', 'git_commits', ['commit_id'], ['id'])
    op.alter_column('metric_files', 'repository_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_constraint(None, 'git_commits', type_='foreignkey')
    op.alter_column('git_commits', 'repository_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('git_commits', 'metric_file_id')
    # ### end Alembic commands ###
