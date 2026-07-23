"""initial schema

Revision ID: 001
Revises: 
Create Date: 2026-07-21 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Enable pgvector
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('oauth_provider', sa.String(length=50), nullable=True),
        sa.Column('oauth_id', sa.String(length=255), nullable=True),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('plan', sa.String(length=20), server_default='free', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # 3. Create images table
    op.create_table(
        'images',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('anon_session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('storage_path', sa.Text(), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('mime_type', sa.String(length=50), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('embedding', Vector(1024), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint(
            '(user_id IS NOT NULL AND anon_session_id IS NULL) OR (user_id IS NULL AND anon_session_id IS NOT NULL)',
            name='images_owner_check'
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_images_user_id', 'images', ['user_id'])
    op.create_index('idx_images_anon_session_id', 'images', ['anon_session_id'])
    op.execute("CREATE INDEX idx_images_embedding ON images USING ivfflat (embedding vector_cosine_ops);")

    # 4. Create captions table
    op.create_table(
        'captions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('image_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('beam_rank', sa.Integer(), server_default='0', nullable=False),
        sa.Column('beam_score', sa.Float(), nullable=True),
        sa.Column('is_edited', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('edited_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['image_id'], ['images.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_captions_image_id', 'captions', ['image_id'])

    # 5. Create caption_feedback table
    op.create_table(
        'caption_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('caption_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rating', sa.String(length=10), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['caption_id'], ['captions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('image_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='queued', nullable=False),
        sa.Column('queue_name', sa.String(length=50), server_default='caption_generation', nullable=True),
        sa.Column('attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['image_id'], ['images.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_jobs_image_id', 'jobs', ['image_id'])

    # 7. Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash')
    )
    op.create_index('idx_api_keys_user_id', 'api_keys', ['user_id'])

    # --- ROW LEVEL SECURITY (RLS) ---
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
    op.execute(
        "CREATE POLICY users_self_access ON users "
        "USING (id = current_setting('app.current_user_id', true)::uuid);"
    )

    op.execute("ALTER TABLE images ENABLE ROW LEVEL SECURITY;")
    op.execute(
        "CREATE POLICY images_owner_access ON images "
        "USING ("
        "   user_id = current_setting('app.current_user_id', true)::uuid "
        "   OR anon_session_id = current_setting('app.current_anon_session_id', true)::uuid"
        ");"
    )

    op.execute("ALTER TABLE captions ENABLE ROW LEVEL SECURITY;")
    op.execute(
        "CREATE POLICY captions_via_image_owner ON captions "
        "USING ("
        "   image_id IN ("
        "       SELECT id FROM images "
        "       WHERE user_id = current_setting('app.current_user_id', true)::uuid "
        "          OR anon_session_id = current_setting('app.current_anon_session_id', true)::uuid"
        "   )"
        ");"
    )

    op.execute("ALTER TABLE caption_feedback ENABLE ROW LEVEL SECURITY;")
    # The policy for feedback owner write
    op.execute(
        "CREATE POLICY feedback_owner_write ON caption_feedback "
        "FOR ALL "
        "USING (user_id = current_setting('app.current_user_id', true)::uuid);"
    )


def downgrade() -> None:
    # Downgrades are normally written in reverse order.
    op.drop_table('api_keys')
    op.drop_table('jobs')
    op.drop_table('caption_feedback')
    op.drop_table('captions')
    op.drop_table('images')
    op.drop_table('users')
    op.execute("DROP EXTENSION IF EXISTS vector;")
