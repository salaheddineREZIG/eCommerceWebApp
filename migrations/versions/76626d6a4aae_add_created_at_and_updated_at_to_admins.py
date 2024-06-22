from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '76626d6a4aae'
down_revision = None
branch_labels = None
depends_on = None

def column_exists(table_name, column_name):
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def upgrade():
    # Add columns created_at and updated_at to admins
    if not column_exists('admins', 'created_at'):
        with op.batch_alter_table('admins') as batch_op:
            batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
    if not column_exists('admins', 'updated_at'):
        with op.batch_alter_table('admins') as batch_op:
            batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))

    # Modify table categories: drop foreign key and column parent_id
    with op.batch_alter_table('categories') as batch_op:
        batch_op.drop_constraint('fk_categories_parent_id', type_='foreignkey')
        batch_op.drop_column('parent_id')

    # Add columns payment_method and tracking_number to orders
    if not column_exists('orders', 'payment_method'):
        with op.batch_alter_table('orders') as batch_op:
            batch_op.add_column(sa.Column('payment_method', sa.String(length=50), nullable=False))
    if not column_exists('orders', 'tracking_number'):
        with op.batch_alter_table('orders') as batch_op:
            batch_op.add_column(sa.Column('tracking_number', sa.String(length=50), nullable=True))

    # Add columns created_at and updated_at to users
    if not column_exists('users', 'created_at'):
        with op.batch_alter_table('users') as batch_op:
            batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False))
    if not column_exists('users', 'updated_at'):
        with op.batch_alter_table('users') as batch_op:
            batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False))

def downgrade():
    # Remove columns created_at and updated_at from users
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')

    # Remove columns payment_method and tracking_number from orders
    with op.batch_alter_table('orders') as batch_op:
        batch_op.drop_column('tracking_number')
        batch_op.drop_column('payment_method')

    # Modify table categories: add back column parent_id and foreign key
    with op.batch_alter_table('categories') as batch_op:
        batch_op.add_column(sa.Column('parent_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_categories_parent_id', 'categories', ['parent_id'], ['id'])

    # Remove columns created_at and updated_at from admins
    with op.batch_alter_table('admins') as batch_op:
        batch_op.drop_column('created_at')
        batch_op.drop_column('updated_at')
