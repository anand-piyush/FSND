"""empty message

Revision ID: 430c62f78e2f
Revises: 78e217ad6c1a
Create Date: 2021-09-23 21:02:33.561170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '430c62f78e2f'
down_revision = '78e217ad6c1a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('actors', 'age',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('actors', 'firstname',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('actors', 'gender',
               existing_type=sa.VARCHAR(length=32),
               nullable=False)
    op.alter_column('actors', 'lastname',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('actors', 'lastname',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('actors', 'gender',
               existing_type=sa.VARCHAR(length=32),
               nullable=True)
    op.alter_column('actors', 'firstname',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('actors', 'age',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
