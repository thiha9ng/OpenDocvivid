import asyncio
from functools import wraps
from typing import Callable, TypeVar, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.models.base import async_session, sync_session


F = TypeVar("F", bound=Callable[..., Any])


def transactional() -> Callable[[F], F]:
    """
    Transaction decorator (supports async & sync):
    - No outer transaction: Start top-level transaction and auto commit/rollback
    - Has outer transaction: Reuse outer transaction directly
    - Automatically manage session lifecycle to prevent connection leaks
    Dependencies:
      - Async: db.async_session() -> AsyncSession (async_scoped_session)
    """

    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            # -------- Async function --------
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                session: AsyncSession = async_session()
        
                in_tx = session.in_transaction()
                if not in_tx:
                    async with session.begin():
                        try:
                            result = await func(*args, **kwargs)
                            return result   
                        except Exception:
                            raise
                else:
                    return await func(*args, **kwargs)

            return async_wrapper

        else:
            # -------- Sync function --------
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                session: Session = sync_session()
                in_tx = session.in_transaction()
                if not in_tx:
                    with session.begin():
                        try:
                            result = func(*args, **kwargs)
                            return result            
                        except Exception:
                            raise
                else:
                    return func(*args, **kwargs)
            return sync_wrapper
    return decorator
