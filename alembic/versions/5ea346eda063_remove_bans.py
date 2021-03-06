"""Remove Bans

Revision ID: 5ea346eda063
Revises: 5f40e81aad01
Create Date: 2020-10-06 14:09:56.906682

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5ea346eda063"
down_revision = "5f40e81aad01"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "host_banned")
    op.drop_column("users", "reports_created_count")
    op.drop_column("users", "report_count")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column("report_count", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "reports_created_count", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "users",
        sa.Column("host_banned", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
    # ### end Alembic commands ###
