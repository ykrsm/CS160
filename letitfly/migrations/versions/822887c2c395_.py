"""empty message

Revision ID: 822887c2c395
Revises: 2dc2514d24e0
Create Date: 2017-11-06 10:26:50.713850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '822887c2c395'
down_revision = '2dc2514d24e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('drives', sa.Column('end_location', sa.String(length=100), nullable=False))
    op.add_column('drives', sa.Column('start_location', sa.String(length=100), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('drives', 'start_location')
    op.drop_column('drives', 'end_location')
    # ### end Alembic commands ###