from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from configs.environment import get_environment_variables
from configs.database import Base
from models.TaskModel import Task
from models.TaskCount import TaskCounter
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_environment_variables()

config.set_main_option(
    'sqlalchemy.url', f"{settings.DATABASE_DIALECT}+psycopg2://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, compare_type=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
        future=True
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
