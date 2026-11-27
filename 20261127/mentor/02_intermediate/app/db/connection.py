"""B-03: SQLAlchemy Connection을 짧은 read-only transaction으로 사용."""
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.services.errors import ServiceError

class Database:
    def __init__(self, settings):
        self.engine = create_engine(settings.database_url, pool_pre_ping=True,
            connect_args={'connect_timeout':5, 'options': f'-c default_transaction_read_only=on -c statement_timeout={settings.db_timeout_ms}'}, hide_parameters=True)
    @contextmanager
    def read(self):
        try:
            with self.engine.connect() as conn, conn.begin():
                # 세션 기본값 외에도 트랜잭션을 명시적으로 읽기 전용으로 강제.
                conn.execute(text('SET TRANSACTION READ ONLY'))
                yield conn
        except SQLAlchemyError:
            raise ServiceError('DB_UNAVAILABLE') from None
    def close(self):
        self.engine.dispose()
