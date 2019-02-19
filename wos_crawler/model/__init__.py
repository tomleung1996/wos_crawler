from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

Base = declarative_base()


def get_engine(db_path=None, db_url=None, echo=False):
    assert (db_path is None and db_url is not None) or (db_path is not None and db_url is None)

    if db_path is not None:
        if not db_path:
            timestamp = str(time.strftime('%Y-%m-%d-%H.%M.%S', time.localtime(time.time())))
            engine = create_engine('sqlite:///wos_crawler_result_{}.db'.format(timestamp), echo=echo)
        else:
            engine = create_engine('sqlite:///{}'.format(db_path), echo=echo)
    else:
        engine = create_engine(db_url, encoding='utf-8')
    return engine


def get_session(engine, auto_flush=True):
    Session = sessionmaker(bind=engine, autoflush=auto_flush)
    session = Session()
    return session
