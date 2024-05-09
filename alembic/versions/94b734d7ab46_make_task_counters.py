"""make task counters

Revision ID: 94b734d7ab46
Revises: 4ca1e67b9ec5
Create Date: 2024-05-07 15:39:09.842323

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94b734d7ab46'
down_revision = '4ca1e67b9ec5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task_counters',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('total_created', sa.Integer(), nullable=True),
    sa.Column('total_completed', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task_counters')
    # ### end Alembic commands ###