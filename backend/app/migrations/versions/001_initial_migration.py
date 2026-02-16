"""Initial migration: create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types (only if they don't exist)
    enums = [
        ("user_role_enum", "('customer', 'sales', 'admin')"),
        ("order_status_enum", "('PENDING_PAYMENT', 'PAYMENT_SUBMITTED', 'PAYMENT_RESUBMIT_REQUESTED', 'PAYMENT_REJECTED', 'PAID', 'PACKING', 'DISPATCHED', 'DELIVERED', 'CANCELLED')"),
        ("payment_method_type_enum", "('BANK_TRANSFER', 'MOBILE_MONEY', 'OTHER')"),
        ("payment_status_enum", "('submitted', 'approved', 'rejected', 'resubmit_requested')"),
        ("notification_type_enum", "('PAYMENT_APPROVED', 'PAYMENT_REJECTED', 'PAYMENT_RESUBMIT_REQUESTED', 'ORDER_STATUS_UPDATED', 'ORDER_DISPATCHED', 'ORDER_DELIVERED', 'NEW_ORDER', 'NEW_PAYMENT_SUBMITTED')"),
        ("otp_type_enum", "('phone', 'email')"),
        ("otp_purpose_enum", "('login', 'verification', 'password_reset')"),
    ]
    
    for enum_name, enum_values in enums:
        op.execute(f"""
            DO $$ BEGIN
                CREATE TYPE {enum_name} AS ENUM {enum_values};
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('phone_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('telegram_user_id', sa.String(100), nullable=True),
        sa.Column('telegram_username', sa.String(100), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('role', postgresql.ENUM('customer', 'sales', 'admin', name='user_role_enum', create_type=False), nullable=False, server_default='customer'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_users_phone', 'users', ['phone'], unique=True, postgresql_where=sa.text('phone IS NOT NULL AND phone_verified = true'))
    op.create_index('idx_users_email', 'users', ['email'], unique=True, postgresql_where=sa.text('email IS NOT NULL AND email_verified = true'))
    op.create_index('idx_users_telegram_user_id', 'users', ['telegram_user_id'], unique=True, postgresql_where=sa.text('telegram_user_id IS NOT NULL'))
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])

    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_categories_slug', 'categories', ['slug'], unique=True)
    op.create_index('idx_categories_parent_id', 'categories', ['parent_id'])
    op.create_index('idx_categories_is_active', 'categories', ['is_active'])

    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category_id', sa.BigInteger(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_products_slug', 'products', ['slug'], unique=True)
    op.create_index('idx_products_category_id', 'products', ['category_id'])
    op.create_index('idx_products_deleted_at', 'products', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NULL'))

    # Create product_variants table
    op.create_table(
        'product_variants',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.BigInteger(), nullable=False),
        sa.Column('label', sa.String(100), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('stock_qty', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sku', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.CheckConstraint('price >= 0', name='check_price_non_negative'),
        sa.CheckConstraint('stock_qty >= 0', name='check_stock_non_negative'),
        sa.UniqueConstraint('product_id', 'label', name='uq_product_variant_label'),
    )
    op.create_index('idx_product_variants_product_id', 'product_variants', ['product_id'])
    op.create_index('idx_product_variants_sku', 'product_variants', ['sku'], unique=True, postgresql_where=sa.text('sku IS NOT NULL'))
    op.create_index('idx_product_variants_is_active', 'product_variants', ['is_active'], postgresql_where=sa.text('is_active = true'))

    # Create product_images table
    op.create_table(
        'product_images',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.BigInteger(), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('alt_text', sa.String(200), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_product_images_product_id', 'product_images', ['product_id'])
    op.create_index('idx_product_images_sort_order', 'product_images', ['product_id', 'sort_order'])

    # Create delivery_zones table
    op.create_table(
        'delivery_zones',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('fee', sa.Numeric(10, 2), nullable=False),
        sa.Column('eta_min_days', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('eta_max_days', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('fee >= 0', name='check_fee_non_negative'),
        sa.CheckConstraint('eta_min_days >= 0', name='check_eta_min_non_negative'),
        sa.CheckConstraint('eta_max_days >= eta_min_days', name='check_eta_max_gte_min'),
    )
    op.create_index('idx_delivery_zones_name', 'delivery_zones', ['name'], unique=True)
    op.create_index('idx_delivery_zones_is_active', 'delivery_zones', ['is_active'], postgresql_where=sa.text('is_active = true'))

    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('order_number', sa.String(20), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING_PAYMENT', 'PAYMENT_SUBMITTED', 'PAYMENT_RESUBMIT_REQUESTED', 'PAYMENT_REJECTED', 'PAID', 'PACKING', 'DISPATCHED', 'DELIVERED', 'CANCELLED', name='order_status_enum', create_type=False), nullable=False, server_default='PENDING_PAYMENT'),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False),
        sa.Column('delivery_fee', sa.Numeric(10, 2), nullable=False),
        sa.Column('total', sa.Numeric(10, 2), nullable=False),
        sa.Column('delivery_zone_id', sa.BigInteger(), nullable=True),
        sa.Column('delivery_address', sa.Text(), nullable=False),
        sa.Column('recipient_name', sa.String(100), nullable=False),
        sa.Column('recipient_phone', sa.String(20), nullable=False),
        sa.Column('delivery_instructions', sa.Text(), nullable=True),
        sa.Column('expected_delivery_from', sa.Date(), nullable=True),
        sa.Column('expected_delivery_to', sa.Date(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['delivery_zone_id'], ['delivery_zones.id'], ondelete='SET NULL'),
        sa.CheckConstraint('subtotal >= 0', name='check_subtotal_non_negative'),
        sa.CheckConstraint('delivery_fee >= 0', name='check_delivery_fee_non_negative'),
        sa.CheckConstraint('total >= 0', name='check_total_non_negative'),
    )
    op.create_index('idx_orders_order_number', 'orders', ['order_number'], unique=True)
    op.create_index('idx_orders_user_id', 'orders', ['user_id'])
    op.create_index('idx_orders_status', 'orders', ['status'])
    op.create_index('idx_orders_created_at', 'orders', ['created_at'])
    op.create_index('idx_orders_delivery_zone_id', 'orders', ['delivery_zone_id'])
    op.create_index('idx_orders_user_status', 'orders', ['user_id', 'status'])
    op.create_index('idx_orders_status_created', 'orders', ['status', 'created_at'])

    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('product_id', sa.BigInteger(), nullable=False),
        sa.Column('variant_id', sa.BigInteger(), nullable=True),
        sa.Column('product_name', sa.String(200), nullable=False),
        sa.Column('variant_label', sa.String(100), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('line_total', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ondelete='SET NULL'),
        sa.CheckConstraint('quantity > 0', name='check_quantity_positive'),
        sa.CheckConstraint('unit_price >= 0', name='check_unit_price_non_negative'),
        sa.CheckConstraint('line_total >= 0', name='check_line_total_non_negative'),
    )
    op.create_index('idx_order_items_order_id', 'order_items', ['order_id'])
    op.create_index('idx_order_items_product_id', 'order_items', ['product_id'])
    op.create_index('idx_order_items_variant_id', 'order_items', ['variant_id'])

    # Create payment_methods table
    op.create_table(
        'payment_methods',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('type', postgresql.ENUM('BANK_TRANSFER', 'MOBILE_MONEY', 'OTHER', name='payment_method_type_enum', create_type=False), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('account_identifier', sa.String(100), nullable=False),
        sa.Column('account_holder', sa.String(100), nullable=False),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_payment_methods_type', 'payment_methods', ['type'])
    op.create_index('idx_payment_methods_is_active', 'payment_methods', ['is_active'], postgresql_where=sa.text('is_active = true'))
    op.create_index('idx_payment_methods_sort_order', 'payment_methods', ['is_active', 'sort_order'], postgresql_where=sa.text('is_active = true'))

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('method_id', sa.BigInteger(), nullable=False),
        sa.Column('submitted_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount_declared', sa.Numeric(10, 2), nullable=True),
        sa.Column('reference_text', sa.String(200), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('screenshot_url', sa.String(500), nullable=False),
        sa.Column('status', postgresql.ENUM('submitted', 'approved', 'rejected', 'resubmit_requested', name='payment_status_enum', create_type=False), nullable=False, server_default='submitted'),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['method_id'], ['payment_methods.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['submitted_by_user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ondelete='SET NULL'),
        sa.CheckConstraint('amount_declared >= 0', name='check_amount_declared_non_negative'),
    )
    op.create_index('idx_payments_order_id', 'payments', ['order_id'])
    op.create_index('idx_payments_method_id', 'payments', ['method_id'])
    op.create_index('idx_payments_status', 'payments', ['status'])
    op.create_index('idx_payments_submitted_by', 'payments', ['submitted_by_user_id'])
    op.create_index('idx_payments_reviewed_by', 'payments', ['reviewed_by'])
    op.create_index('idx_payments_created_at', 'payments', ['created_at'])
    op.create_index('idx_payments_status_created', 'payments', ['status', 'created_at'], postgresql_where=sa.text("status = 'submitted'"))

    # Create order_status_history table
    op.create_table(
        'order_status_history',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('old_status', postgresql.ENUM('PENDING_PAYMENT', 'PAYMENT_SUBMITTED', 'PAYMENT_RESUBMIT_REQUESTED', 'PAYMENT_REJECTED', 'PAID', 'PACKING', 'DISPATCHED', 'DELIVERED', 'CANCELLED', name='order_status_enum', create_type=False), nullable=True),
        sa.Column('new_status', postgresql.ENUM('PENDING_PAYMENT', 'PAYMENT_SUBMITTED', 'PAYMENT_RESUBMIT_REQUESTED', 'PAYMENT_REJECTED', 'PAID', 'PACKING', 'DISPATCHED', 'DELIVERED', 'CANCELLED', name='order_status_enum', create_type=False), nullable=False),
        sa.Column('actor_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_order_status_history_order_id', 'order_status_history', ['order_id'])
    op.create_index('idx_order_status_history_created_at', 'order_status_history', ['created_at'])
    op.create_index('idx_order_status_history_order_created', 'order_status_history', ['order_id', 'created_at'])

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', postgresql.ENUM('PAYMENT_APPROVED', 'PAYMENT_REJECTED', 'PAYMENT_RESUBMIT_REQUESTED', 'ORDER_STATUS_UPDATED', 'ORDER_DISPATCHED', 'ORDER_DELIVERED', 'NEW_ORDER', 'NEW_PAYMENT_SUBMITTED', name='notification_type_enum', create_type=False), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('related_order_id', sa.BigInteger(), nullable=True),
        sa.Column('related_payment_id', sa.BigInteger(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['related_order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['related_payment_id'], ['payments.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('idx_notifications_is_read', 'notifications', ['user_id', 'is_read'], postgresql_where=sa.text('is_read = false'))
    op.create_index('idx_notifications_created_at', 'notifications', ['created_at'])
    op.create_index('idx_notifications_related_order', 'notifications', ['related_order_id'])
    op.create_index('idx_notifications_related_payment', 'notifications', ['related_payment_id'])

    # Create otp_codes table
    op.create_table(
        'otp_codes',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('identifier', sa.String(255), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('type', postgresql.ENUM('phone', 'email', name='otp_type_enum', create_type=False), nullable=False),
        sa.Column('purpose', postgresql.ENUM('login', 'verification', 'password_reset', name='otp_purpose_enum', create_type=False), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_otp_codes_identifier', 'otp_codes', ['identifier'])
    op.create_index('idx_otp_codes_code', 'otp_codes', ['code'])
    op.create_index('idx_otp_codes_expires_at', 'otp_codes', ['expires_at'])
    op.create_index('idx_otp_codes_identifier_type', 'otp_codes', ['identifier', 'type', 'expires_at'], postgresql_where=sa.text('used_at IS NULL'))

    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(500), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_refresh_tokens_token', 'refresh_tokens', ['token'], unique=True)
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('idx_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'])

    # Create updated_at trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Apply updated_at triggers to relevant tables
    for table in ['users', 'categories', 'products', 'product_variants', 'delivery_zones', 'orders', 'payment_methods', 'payments']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # Drop triggers
    for table in ['users', 'categories', 'products', 'product_variants', 'delivery_zones', 'orders', 'payment_methods', 'payments']:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};")
    
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop tables in reverse order
    op.drop_table('refresh_tokens')
    op.drop_table('otp_codes')
    op.drop_table('notifications')
    op.drop_table('order_status_history')
    op.drop_table('payments')
    op.drop_table('payment_methods')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('delivery_zones')
    op.drop_table('product_images')
    op.drop_table('product_variants')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_table('users')

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS otp_purpose_enum")
    op.execute("DROP TYPE IF EXISTS otp_type_enum")
    op.execute("DROP TYPE IF EXISTS notification_type_enum")
    op.execute("DROP TYPE IF EXISTS payment_status_enum")
    op.execute("DROP TYPE IF EXISTS payment_method_type_enum")
    op.execute("DROP TYPE IF EXISTS order_status_enum")
    op.execute("DROP TYPE IF EXISTS user_role_enum")

