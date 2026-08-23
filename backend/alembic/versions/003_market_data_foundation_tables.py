"""Market Data Foundation Tables

Revision ID: 003
Revises: 002
Create Date: 2026-08-23

"""
import uuid
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create crypto_assets table
    op.create_table(
        'crypto_assets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('provider_id', sa.String(length=100), nullable=False),
        sa.Column('asset_type', sa.String(length=20), nullable=False, server_default='crypto'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol', 'provider_id', name='uq_asset_symbol_provider')
    )
    op.create_index(op.f('ix_crypto_assets_id'), 'crypto_assets', ['id'], unique=False)
    op.create_index(op.f('ix_crypto_assets_symbol'), 'crypto_assets', ['symbol'], unique=False)
    op.create_index(op.f('ix_crypto_assets_slug'), 'crypto_assets', ['slug'], unique=False)
    op.create_index(op.f('ix_crypto_assets_provider_id'), 'crypto_assets', ['provider_id'], unique=False)
    op.create_index(op.f('ix_crypto_assets_status'), 'crypto_assets', ['status'], unique=False)
    op.create_index(op.f('ix_crypto_assets_is_active'), 'crypto_assets', ['is_active'], unique=False)

    # 2. Create market_snapshots table
    op.create_table(
        'market_snapshots',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('asset_id', sa.String(length=36), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('market_cap', sa.Float(), nullable=True),
        sa.Column('volume_24h', sa.Float(), nullable=True),
        sa.Column('price_change_24h', sa.Float(), nullable=True),
        sa.Column('price_change_percentage_24h', sa.Float(), nullable=True),
        sa.Column('high_24h', sa.Float(), nullable=True),
        sa.Column('low_24h', sa.Float(), nullable=True),
        sa.Column('circulating_supply', sa.Float(), nullable=True),
        sa.Column('total_supply', sa.Float(), nullable=True),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='unknown'),
        sa.Column('data_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ingested_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['asset_id'], ['crypto_assets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_snapshots_id'), 'market_snapshots', ['id'], unique=False)
    op.create_index(op.f('ix_market_snapshots_asset_id'), 'market_snapshots', ['asset_id'], unique=False)
    op.create_index(op.f('ix_market_snapshots_data_timestamp'), 'market_snapshots', ['data_timestamp'], unique=False)
    op.create_index('ix_snapshot_asset_timestamp', 'market_snapshots', ['asset_id', 'data_timestamp'], unique=False)

    # 3. Create ohlcv_candles table
    op.create_table(
        'ohlcv_candles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('asset_id', sa.String(length=36), nullable=False),
        sa.Column('timeframe', sa.String(length=10), nullable=False),
        sa.Column('open', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('candle_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='unknown'),
        sa.Column('ingested_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['asset_id'], ['crypto_assets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_id', 'timeframe', 'candle_timestamp', 'provider', name='uq_candle_asset_tf_ts_prov')
    )
    op.create_index(op.f('ix_ohlcv_candles_id'), 'ohlcv_candles', ['id'], unique=False)
    op.create_index(op.f('ix_ohlcv_candles_asset_id'), 'ohlcv_candles', ['asset_id'], unique=False)
    op.create_index(op.f('ix_ohlcv_candles_timeframe'), 'ohlcv_candles', ['timeframe'], unique=False)
    op.create_index(op.f('ix_ohlcv_candles_candle_timestamp'), 'ohlcv_candles', ['candle_timestamp'], unique=False)
    op.create_index('ix_ohlcv_asset_tf_ts', 'ohlcv_candles', ['asset_id', 'timeframe', 'candle_timestamp'], unique=False)

    # 4. Seed Standard Crypto Assets
    assets_table = sa.table(
        'crypto_assets',
        sa.column('id', sa.String),
        sa.column('symbol', sa.String),
        sa.column('name', sa.String),
        sa.column('slug', sa.String),
        sa.column('provider_id', sa.String),
        sa.column('asset_type', sa.String),
        sa.column('status', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('rank', sa.Integer),
    )
    op.bulk_insert(
        assets_table,
        [
            {'id': str(uuid.uuid4()), 'symbol': 'BTC', 'name': 'Bitcoin', 'slug': 'bitcoin', 'provider_id': 'bitcoin', 'asset_type': 'crypto', 'status': 'active', 'is_active': True, 'rank': 1},
            {'id': str(uuid.uuid4()), 'symbol': 'ETH', 'name': 'Ethereum', 'slug': 'ethereum', 'provider_id': 'ethereum', 'asset_type': 'crypto', 'status': 'active', 'is_active': True, 'rank': 2},
            {'id': str(uuid.uuid4()), 'symbol': 'SOL', 'name': 'Solana', 'slug': 'solana', 'provider_id': 'solana', 'asset_type': 'crypto', 'status': 'active', 'is_active': True, 'rank': 3},
            {'id': str(uuid.uuid4()), 'symbol': 'BNB', 'name': 'BNB', 'slug': 'binancecoin', 'provider_id': 'binancecoin', 'asset_type': 'crypto', 'status': 'active', 'is_active': True, 'rank': 4},
            {'id': str(uuid.uuid4()), 'symbol': 'XRP', 'name': 'XRP', 'slug': 'ripple', 'provider_id': 'ripple', 'asset_type': 'crypto', 'status': 'active', 'is_active': True, 'rank': 5},
            {'id': str(uuid.uuid4()), 'symbol': 'ADA', 'name': 'Cardano', 'slug': 'cardano', 'provider_id': 'cardano', 'asset_type': 'crypto', 'status': 'active', 'is_active': True, 'rank': 6},
            {'id': str(uuid.uuid4()), 'symbol': 'AVAX', 'name': 'Avalanche', 'slug': 'avalanche-2', 'provider_id': 'avalanche-2', 'asset_type': 'crypto', 'status': 'active', 'is_active': True, 'rank': 7},
            {'id': str(uuid.uuid4()), 'symbol': 'DOT', 'name': 'Polkadot', 'slug': 'polkadot', 'provider_id': 'polkadot', 'asset_type': 'crypto', 'status': 'active', 'is_active': True, 'rank': 8},
            {'id': str(uuid.uuid4()), 'symbol': 'LINK', 'name': 'Chainlink', 'slug': 'chainlink', 'provider_id': 'chainlink', 'asset_type': 'crypto', 'status': 'active', 'is_active': True, 'rank': 9},
            {'id': str(uuid.uuid4()), 'symbol': 'MATIC', 'name': 'Polygon', 'slug': 'matic-network', 'provider_id': 'matic-network', 'asset_type': 'crypto', 'status': 'active', 'is_active': True, 'rank': 10},
        ]
    )

def downgrade() -> None:
    op.drop_table('ohlcv_candles')
    op.drop_table('market_snapshots')
    op.drop_table('crypto_assets')
