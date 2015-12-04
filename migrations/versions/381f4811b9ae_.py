"""empty message

Revision ID: 381f4811b9ae
Revises: None
Create Date: 2015-12-02 14:47:57.391454

"""

# revision identifiers, used by Alembic.
revision = '381f4811b9ae'
down_revision = None

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy_searchable import sync_trigger, vectorizer

def upgrade():
    vectorizer.clear()

    conn = op.get_bind()
    op.add_column('groups', sa.Column('name', HSTORE))

    metadata = sa.MetaData(bind=conn)
    groups = sa.Table('groups', metadata, autoload=True)

    @vectorizer(groups.c.name)
    def hstore_vectorizer(column):
        return sa.cast(sa.func.avals(column), sa.Text)

    op.add_column('groups', sa.Column('description', sa.Text))
    sync_trigger(
        conn,
        'groups',
        'search_vector',
        ['name', 'description'],
        metadata=metadata
    )

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comment_likes')
    op.drop_table('post_likes')
    op.drop_table('group_posts')
    op.drop_table('comments')
    op.drop_table('association_table')
    op.drop_table('posts')
    op.drop_table('messages')
    op.drop_table('members')
    op.drop_table('friends')
    op.drop_table('friend_requests')
    op.drop_table('admins')
    op.drop_table('users')
    op.drop_index('ix_groups_search_vector', table_name='groups')
    op.drop_table('groups')
    ### end Alembic commands ###
