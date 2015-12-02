"""empty message

Revision ID: 52243d5f289c
Revises: 8289101ee1d
Create Date: 2015-12-02 10:14:32.906556

"""

# revision identifiers, used by Alembic.
revision = '52243d5f289c'
down_revision = '8289101ee1d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('self_post', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'self_post')
    ### end Alembic commands ###