"""add cascade delete to document chunks

Revision ID: d2feeaf9fb8c
Revises: a79f3305591f
Create Date: 2026-10-03 12:55:58.268944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2feeaf9fb8c'
down_revision: Union[str, Sequence[str], None] = 'a79f3305591f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "document_chunks_document_id_fkey",
        "document_chunks",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "fk_document_chunks_document_id_documents",
        "document_chunks",
        "documents",
        ["document_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_document_chunks_document_id_documents",
        "document_chunks",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "document_chunks_document_id_fkey",
        "document_chunks",
        "documents",
        ["document_id"],
        ["id"],
    )