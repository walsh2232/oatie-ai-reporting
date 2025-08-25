"""create table metadata

Revision ID: 0001_create_table_metadata
Revises: 
Create Date: 2025-08-24 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_table_metadata'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create table_metadata table
    op.create_table('table_metadata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('schema_name', sa.String(length=100), nullable=False),
    sa.Column('table_name', sa.String(length=200), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_table_metadata_schema_name'), 'table_metadata', ['schema_name'], unique=False)
    op.create_index(op.f('ix_table_metadata_table_name'), 'table_metadata', ['table_name'], unique=False)
    op.create_index('ix_schema_table', 'table_metadata', ['schema_name', 'table_name'], unique=False)

def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_schema_table', table_name='table_metadata')
    op.drop_index(op.f('ix_table_metadata_table_name'), table_name='table_metadata')
    op.drop_index(op.f('ix_table_metadata_schema_name'), table_name='table_metadata')
    
    # Drop table
    op.drop_table('table_metadata')
