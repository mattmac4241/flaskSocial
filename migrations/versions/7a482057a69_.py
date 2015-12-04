"""empty message

Revision ID: 7a482057a69
Revises: 381f4811b9ae
Create Date: 2015-12-03 13:33:01.638199

"""

# revision identifiers, used by Alembic.
revision = '7a482057a69'
down_revision = '381f4811b9ae'

from alembic import op
import sqlalchemy as sa



from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy_searchable import sync_trigger, vectorizer

def upgrade():
    vectorizer.clear()

    conn = op.get_bind()
    op.add_column('groups', sa.Column('name_translations', HSTORE))

    metadata = sa.MetaData(bind=conn)
    groups = sa.Table('description', metadata, autoload=True)

    @vectorizer(groups.c.name)
    def hstore_vectorizer(column):
        return sa.cast(sa.func.avals(column), sa.Text)

    op.add_column('groups', sa.Column('description', sa.Text))
    sync_trigger(
        conn,
        'groups',
        'search_vector',
        ['name_translations', 'description'],
        metadata=metadata
    )
    ### end Alembic commands ###


    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('group_requests')
    ### end Alembic commands ###
