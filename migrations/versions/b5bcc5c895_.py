"""empty message

Revision ID: b5bcc5c895
Revises: None
Create Date: 2015-12-03 19:51:43.490486

"""

# revision identifiers, used by Alembic.
revision = 'b5bcc5c895'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comment_likes')
    op.drop_table('admins')
    op.drop_table('members')
    op.drop_table('association_table')
    op.drop_table('post_likes')
    op.drop_table('group_posts')
    op.drop_table('friends')
    op.drop_constraint(u'comments_parent_fkey', 'comments', type_='foreignkey')
    op.drop_constraint(u'comments_poster_fkey', 'comments', type_='foreignkey')
    op.drop_column('comments', 'content')
    op.drop_column('comments', 'poster')
    op.drop_column('comments', 'time_posted')
    op.drop_column('comments', 'poster_name')
    op.drop_column('comments', 'parent')
    op.drop_constraint(u'friend_requests_user_sent_to_fkey', 'friend_requests', type_='foreignkey')
    op.drop_constraint(u'friend_requests_user_sent_from_fkey', 'friend_requests', type_='foreignkey')
    op.drop_column('friend_requests', 'user_sent_to')
    op.drop_column('friend_requests', 'accepted')
    op.drop_column('friend_requests', 'user_sent_from')
    op.drop_constraint(u'group_requests_group_fkey', 'group_requests', type_='foreignkey')
    op.drop_constraint(u'group_requests_user_fkey', 'group_requests', type_='foreignkey')
    op.drop_column('group_requests', 'accepted')
    op.drop_column('group_requests', 'group')
    op.drop_column('group_requests', 'user')
    op.drop_constraint(u'groups_name_key', 'groups', type_='unique')
    op.drop_index('ix_groups_search_vector', table_name='groups')
    op.drop_column('groups', 'search_vector')
    op.drop_column('groups', 'name')
    op.drop_column('groups', 'private')
    op.drop_column('groups', 'description')
    op.drop_constraint(u'messages_user_to_fkey', 'messages', type_='foreignkey')
    op.drop_constraint(u'messages_user_from_fkey', 'messages', type_='foreignkey')
    op.drop_column('messages', 'user_to')
    op.drop_column('messages', 'read')
    op.drop_column('messages', 'content')
    op.drop_column('messages', 'user_from')
    op.drop_constraint(u'posts_group_fkey', 'posts', type_='foreignkey')
    op.drop_constraint(u'posts_poster_fkey', 'posts', type_='foreignkey')
    op.drop_column('posts', 'self_post')
    op.drop_column('posts', 'group')
    op.drop_column('posts', 'title')
    op.drop_column('posts', 'poster')
    op.drop_column('posts', 'time_posted')
    op.drop_column('posts', 'poster_name')
    op.drop_column('posts', 'content')
    op.drop_constraint(u'users_email_key', 'users', type_='unique')
    op.drop_constraint(u'users_user_name_key', 'users', type_='unique')
    op.drop_column('users', 'password')
    op.drop_column('users', 'user_name')
    op.drop_column('users', 'email')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('user_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('password', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.create_unique_constraint(u'users_user_name_key', 'users', ['user_name'])
    op.create_unique_constraint(u'users_email_key', 'users', ['email'])
    op.add_column('posts', sa.Column('content', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('posts', sa.Column('poster_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('posts', sa.Column('time_posted', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('posts', sa.Column('poster', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('posts', sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('posts', sa.Column('group', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('posts', sa.Column('self_post', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.create_foreign_key(u'posts_poster_fkey', 'posts', 'users', ['poster'], ['id'])
    op.create_foreign_key(u'posts_group_fkey', 'posts', 'groups', ['group'], ['id'])
    op.add_column('messages', sa.Column('user_from', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('messages', sa.Column('content', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('messages', sa.Column('read', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('messages', sa.Column('user_to', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(u'messages_user_from_fkey', 'messages', 'users', ['user_from'], ['id'])
    op.create_foreign_key(u'messages_user_to_fkey', 'messages', 'users', ['user_to'], ['id'])
    op.add_column('groups', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('groups', sa.Column('private', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('groups', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('groups', sa.Column('search_vector', postgresql.TSVECTOR(), autoincrement=False, nullable=True))
    op.create_index('ix_groups_search_vector', 'groups', ['search_vector'], unique=False)
    op.create_unique_constraint(u'groups_name_key', 'groups', ['name'])
    op.add_column('group_requests', sa.Column('user', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('group_requests', sa.Column('group', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('group_requests', sa.Column('accepted', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.create_foreign_key(u'group_requests_user_fkey', 'group_requests', 'users', ['user'], ['id'])
    op.create_foreign_key(u'group_requests_group_fkey', 'group_requests', 'groups', ['group'], ['id'])
    op.add_column('friend_requests', sa.Column('user_sent_from', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('friend_requests', sa.Column('accepted', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('friend_requests', sa.Column('user_sent_to', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(u'friend_requests_user_sent_from_fkey', 'friend_requests', 'users', ['user_sent_from'], ['id'])
    op.create_foreign_key(u'friend_requests_user_sent_to_fkey', 'friend_requests', 'users', ['user_sent_to'], ['id'])
    op.add_column('comments', sa.Column('parent', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('comments', sa.Column('poster_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('comments', sa.Column('time_posted', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('comments', sa.Column('poster', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('comments', sa.Column('content', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.create_foreign_key(u'comments_poster_fkey', 'comments', 'users', ['poster'], ['id'])
    op.create_foreign_key(u'comments_parent_fkey', 'comments', 'posts', ['parent'], ['id'])
    op.create_table('friends',
    sa.Column('friend1_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('friend2_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['friend1_id'], [u'users.id'], name=u'friends_friend1_id_fkey'),
    sa.ForeignKeyConstraint(['friend2_id'], [u'users.id'], name=u'friends_friend2_id_fkey')
    )
    op.create_table('group_posts',
    sa.Column('group_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('post_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['group_id'], [u'groups.id'], name=u'group_posts_group_id_fkey'),
    sa.ForeignKeyConstraint(['post_id'], [u'posts.id'], name=u'group_posts_post_id_fkey')
    )
    op.create_table('post_likes',
    sa.Column('post_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['post_id'], [u'posts.id'], name=u'post_likes_post_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], [u'users.id'], name=u'post_likes_user_id_fkey')
    )
    op.create_table('association_table',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('post_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['post_id'], [u'users.id'], name=u'association_table_post_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], [u'posts.id'], name=u'association_table_user_id_fkey')
    )
    op.create_table('members',
    sa.Column('group_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['group_id'], [u'groups.id'], name=u'members_group_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], [u'users.id'], name=u'members_user_id_fkey')
    )
    op.create_table('admins',
    sa.Column('group_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['group_id'], [u'groups.id'], name=u'admins_group_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], [u'users.id'], name=u'admins_user_id_fkey')
    )
    op.create_table('comment_likes',
    sa.Column('comment_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['comment_id'], [u'comments.id'], name=u'comment_likes_comment_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], [u'users.id'], name=u'comment_likes_user_id_fkey')
    )
    ### end Alembic commands ###
