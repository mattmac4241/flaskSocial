import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy_searchable import sync_trigger, vectorizer

def upgrade():
    vectorizer.clear()

    conn = op.get_bind()
    op.add_column('groups', sa.Column('title', HSTORE))

    metadata = sa.MetaData(bind=conn)
    articles = sa.Table('groups', metadata, autoload=True)

    @vectorizer(articles.c.name_translations)
    def hstore_vectorizer(column):
        return sa.cast(sa.func.avals(column), sa.Text)

    op.add_column('groups', sa.Column('content', sa.Text))
    sync_trigger(
        conn,
        'groups',
        'search_vector',
        ['title', 'content'],
        metadata=metadata
    )
upgrade()
