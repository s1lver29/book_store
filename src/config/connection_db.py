from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .settings import settings

database_url: str | None = settings.database_url

if database_url is None:
    raise ValueError("DATABASE_URL must not be None")

__engine = create_async_engine(database_url, echo=True)

__async_session = async_sessionmaker(__engine, expire_on_commit=False)


async def async_database_session():  # type: ignore
    session: AsyncSession = __async_session()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()
