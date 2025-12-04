"""
Alembic Migration Environment Configuration

This file is the bridge between Alembic and your SQLAlchemy models.
It tells Alembic how to:
- Connect to your database
- Find your model definitions
- Run migrations (both online and offline modes)

Alembic calls functions in this file automatically when you run commands like:
- alembic revision --autogenerate -m "add users table"
- alembic upgrade head

You rarely need to modify this file unless you're doing something special
with your database setup.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add parent directory to path so we can import our backend code
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import your SQLAlchemy Base and settings
from backend.database import Base
from backend.config import settings

# This is the Alembic Config object
config = context.config

# Set the database URL from our settings
# This allows us to use the DATABASE_URL environment variable
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

# Interpret the config file for Python logging
# This sets up loggers basically
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
# This lets Alembic detect changes in your models automatically
target_metadata = Base.metadata

# Import all models here so Alembic can detect them
# Importing the models package will import all models automatically
from backend.models import User, Alert, Brand, Category, ItemHistory


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is also acceptable here. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    Used for generating SQL scripts without connecting to the database.
    Example: alembic upgrade head --sql > migration.sql
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a
    connection with the context.

    This is the normal mode - it actually connects to your database
    and applies the migrations.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Alembic calls this function to run migrations
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
